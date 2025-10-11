# Dockerfile
FROM python:3.9-slim
LABEL authors="ogahserge"

# Réglages Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    # Django collectstatic non-interactif par défaut
    DJANGO_COLLECTSTATIC=1

WORKDIR /afriqconsulting

# Système (ajustez selon vos besoins: psycopg2, GDAL…)
# libgdal + headers pour compat GDAL/python si utilisé
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    libpq-dev \
    libgdal-dev \
    gdal-bin \
  && rm -rf /var/lib/apt/lists/*

# Venv + pip récent
RUN python3 -m venv $VIRTUAL_ENV && pip install --upgrade pip wheel setuptools

# Dépendances Python
COPY requirements.txt /afriqconsulting/requirements.txt
RUN "$VIRTUAL_ENV/bin/python" -m pip install --no-cache-dir -r requirements.txt


# Copie du projet
COPY . /afriqconsulting/

# Prépare les dossiers (écrasés plus tard par des volumes, mais OK en build)
RUN mkdir -p /afriqconsulting/static /afriqconsulting/staticfiles /afriqconsulting/media /afriqconsulting/logs

# (Option) utilisateur non-root pour de meilleures pratiques
# NOTE: si vous gardez la monture locale (.), les permissions doivent suivre.
RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /afriqconsulting
USER appuser

# Expose port
EXPOSE 8000

# Entrypoint (migrations/collectstatic selon env)
COPY entrypoint.sh /entrypoint.sh
USER root
RUN chmod +x /entrypoint.sh && chown appuser:appuser /entrypoint.sh
USER appuser

ENTRYPOINT ["/entrypoint.sh"]

# Commande par défaut : Gunicorn (surchargée par docker-compose.yml si besoin)
CMD ["gunicorn", "afriqconsulting.wsgi:application", "--bind=0.0.0.0:8000", "--workers=4", "--timeout=180", "--log-level=info", "--access-logfile=/afriqconsulting/logs/gunicorn.access.log", "--error-logfile=/afriqconsulting/logs/gunicorn.error.log"]