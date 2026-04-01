"""Configuracion de pruebas local (sin MySQL) para ejecutar test suite en desarrollo."""

from .settings import *  # noqa: F401,F403

# Base SQLite para evitar dependencia de mysqlclient en pruebas locales.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

# Capa de canales en memoria para tests.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# Cache en memoria para evitar Redis en entorno local de pruebas.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Backends livianos para pruebas.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Acelera ejecucion de tests evitando logs verbosos de seguridad.
SECURITY_MIDDLEWARE_LOG_ONLY = True
