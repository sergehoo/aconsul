#!/usr/bin/env bash
set -Eeuo pipefail

log() { echo "[$(date '+%F %T')] $*"; }

# === Paramètres/valeurs par défaut ===
: "${DJANGO_SETTINGS_MODULE:=afriqconsulting.settings}"
: "${RUN_MIGRATIONS:=1}"         # 1 pour exécuter `migrate`
: "${RUN_COLLECTSTATIC:=1}"       # 1 pour exécuter `collectstatic`
: "${RUN_CHECKS:=0}"              # 1 pour `check --deploy`
: "${CREATE_SUPERUSER:=0}"        # 1 pour créer un superuser si non existant

# Dossiers standards du projet (ajuste si besoin)
APP_DIR="/afriqconsulting"
STATIC_DIR="${APP_DIR}/static"
STATICFILES_DIR="${APP_DIR}/staticfiles"
MEDIA_DIR="${APP_DIR}/media"
LOGS_DIR="${APP_DIR}/logs"

# === Attente optionnelle d'un service en amont (ex: Postgres) ===
# Ex: WAIT_FOR_HOST=sighdb WAIT_FOR_PORT=5432
if [[ -n "${WAIT_FOR_HOST:-}" && -n "${WAIT_FOR_PORT:-}" ]]; then
  log "⏳ Waiting for ${WAIT_FOR_HOST}:${WAIT_FOR_PORT}..."
  # nc (netcat) si dispo, sinon fallback /dev/tcp
  if command -v nc >/dev/null 2>&1; then
    until nc -z "${WAIT_FOR_HOST}" "${WAIT_FOR_PORT}"; do sleep 1; done
  else
    while ! (echo >"/dev/tcp/${WAIT_FOR_HOST}/${WAIT_FOR_PORT}") >/dev/null 2>&1; do sleep 1; done
  fi
  log "✅ ${WAIT_FOR_HOST}:${WAIT_FOR_PORT} is up."
fi

# === Préparation des dossiers ===
mkdir -p "$STATIC_DIR" "$STATICFILES_DIR" "$MEDIA_DIR" "$LOGS_DIR"

# Permissions minimales (évite les chown/chmod récursifs coûteux)
chmod u+rwX "$STATIC_DIR" "$STATICFILES_DIR" "$MEDIA_DIR" "$LOGS_DIR" || true

# Fichiers de logs utiles pour Gunicorn (si tu logs vers fichiers)
touch "${LOGS_DIR}/gunicorn.access.log" "${LOGS_DIR}/gunicorn.error.log" || true

# Infos runtime
python - <<'PY' || true
import sys, platform
print("Python:", sys.version)
print("Platform:", platform.platform())
PY

# === Sanity checks Django (optionnel) ===
if [[ "${RUN_CHECKS}" = "1" ]]; then
  log "🔎 Django checks (deploy)..."
  python manage.py check --deploy || { log "❌ Django checks failed"; exit 1; }
fi

# === Migrations ===
if [[ "${RUN_MIGRATIONS}" = "1" ]]; then
  log "🚀 Running migrations..."
  python manage.py migrate --noinput
else
  log "⏭️  Migrations skipped (RUN_MIGRATIONS=${RUN_MIGRATIONS})"
fi

# === Collectstatic ===
if [[ "${RUN_COLLECTSTATIC}" = "1" ]]; then
  log "📦 Collecting static files..."
  python manage.py collectstatic --noinput
else
  log "⏭️  Collectstatic skipped (RUN_COLLECTSTATIC=${RUN_COLLECTSTATIC})"
fi

# === Création superuser optionnelle (idempotente) ===
# Variables attendues si CREATE_SUPERUSER=1 :
#   DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
if [[ "${CREATE_SUPERUSER}" = "1" ]]; then
  : "${DJANGO_SUPERUSER_USERNAME:?DJANGO_SUPERUSER_USERNAME requis}"
  : "${DJANGO_SUPERUSER_EMAIL:?DJANGO_SUPERUSER_EMAIL requis}"
  : "${DJANGO_SUPERUSER_PASSWORD:?DJANGO_SUPERUSER_PASSWORD requis}"
  log "👤 Ensuring Django superuser '${DJANGO_SUPERUSER_USERNAME}' exists..."
  python manage.py shell <<PY
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ["DJANGO_SUPERUSER_USERNAME"]
email = os.environ["DJANGO_SUPERUSER_EMAIL"]
password = os.environ["DJANGO_SUPERUSER_PASSWORD"]
u, created = User.objects.get_or_create(username=username, defaults={"email": email, "is_superuser": True, "is_staff": True})
if created:
    u.set_password(password)
    u.save()
    print("Superuser created.")
else:
    print("Superuser already exists.")
PY
else
  log "⏭️  Superuser creation skipped (CREATE_SUPERUSER=${CREATE_SUPERUSER})"
fi

log "✅ Starting app: $*"
exec "$@"