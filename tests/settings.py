from pathlib import Path

DEBUG = True
USE_TZ = True

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent
# django_wtf/
APPS_DIR = ROOT_DIR / "django_admin_shellx"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "very-secret"

ADMIN_URL = "admin/"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "tests.urls"

DJANGO_APPS = [
    "daphne",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_extensions",
]  # type: ignore

LOCAL_APPS = [
    "django_admin_shellx",
    "django_admin_shellx_custom_admin.apps.CustomAdminConfig",
    "tests",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

SITE_ID = 1
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    str(APPS_DIR / "static"),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(__file__).parent / "media"

ASGI_APPLICATION = "tests.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "webpack_bundles/",
        "CACHE": not DEBUG,
        "STATS_FILE": str(ROOT_DIR / "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    }
}

DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY = True
DJANGO_ADMIN_SHELLX_COMMAND = [
    ["./manage.py", "shell_plus"],
    ["./manage.py", "shell"],
    ["/bin/bash"],
]
DJANGO_ADMIN_SHELLX_WS_PORT = None
