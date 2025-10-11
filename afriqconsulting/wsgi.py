# afriqconsulting/afriqconsulting/wsgi.py
import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings

# Respecte l'ENV, fallback sur prod
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "afriqconsulting.settings.prod")
)

application = get_wsgi_application()

# WhiteNoise est préférable en middleware.
# Si tu veux garder l’enrobage WSGI, fais-le proprement:
try:
    from whitenoise import WhiteNoise
    application = WhiteNoise(application, root=getattr(settings, "STATIC_ROOT", None))
except Exception:
    # WhiteNoise non installé ou STATIC_ROOT absent : ignore
    pass