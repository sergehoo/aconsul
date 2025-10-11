from .base import *
from decouple import config

DEBUG = False

# Autorise la sonde (127.0.0.1) et tes domaines. Pilote via .env si tu veux.
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost,afriqconsulting.com,www.afriqconsulting.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Confiance dans les en-têtes Traefik pour HTTPS
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Redirection HTTPS (optionnel mais recommandé en prod)
SECURE_SSL_REDIRECT = True

# CSRF/CORS (pointe sur ton domaine HTTPS) — pilote via .env
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://afriqconsulting.com,https://www.afriqconsulting.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://afriqconsulting.com,https://www.afriqconsulting.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Base de données actuelle: SQLite (monte bien le fichier via docker-compose)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}