#!/usr/bin/env bash
set -e

# Attente optionnelle d'un service (ex: Postgres) :
# if [ -n "${WAIT_FOR_HOST}" ] && [ -n "${WAIT_FOR_PORT}" ]; then
#   echo "⏳ Waiting for ${WAIT_FOR_HOST}:${WAIT_FOR_PORT}..."
#   until nc -z ${WAIT_FOR_HOST} ${WAIT_FOR_PORT}; do sleep 1; done
# fi

# Migrations (si demandé)
if [ "${RUN_MIGRATIONS}" = "1" ]; then
  echo "🚀 Running migrations..."
  python manage.py migrate --noinput
fi

# Collectstatic (si demandé)
if [ "${RUN_COLLECTSTATIC}" = "1" ]; then
  echo "📦 Collecting static files..."
  python manage.py collectstatic --noinput
fi

echo "✅ Starting app: $*"
exec "$@"