from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "splitwisely-local-development-key"
DEBUG = True
ROOT_URLCONF = "trip.urls"
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = ["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "django.contrib.staticfiles", "trip"]
MIDDLEWARE = ["django.middleware.common.CommonMiddleware", "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware"]
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "trip" / "templates"], "APP_DIRS": True, "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth"]}}]
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "trip" / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "splitwisely.sqlite3"}}
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"
AUTHENTICATION_BACKENDS = ["trip.authentication.EmailOrUsernameBackend"]