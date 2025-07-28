# settings.py

from pathlib import Path
import os
import google.generativeai as genai

# ─────────────────────────────────────────────────────────────────────────────
# 1. Base directory, secret, debug, hosts
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-…'
DEBUG = True
ALLOWED_HOSTS = []

# ─────────────────────────────────────────────────────────────────────────────
# 2. Installed apps & middleware
# ─────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'generator',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'generator.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'circulargen.urls'

# ─────────────────────────────────────────────────────────────────────────────
# 3. Templates
# ─────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'generator' / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'circulargen.wsgi.application'

# ─────────────────────────────────────────────────────────────────────────────
# 4. Database
# ─────────────────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# 5. Password validation
# ─────────────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────────────────────────────────────
# 6. Internationalization & time zone
# ─────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ─────────────────────────────────────────────────────────────────────────────
# 7. Static files
# ─────────────────────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'static' ]
STATIC_ROOT = BASE_DIR / 'staticfiles_root'


# ─────────────────────────────────────────────────────────────────────────────
# 8. Email (SMTP) settings
# ─────────────────────────────────────────────────────────────────────────────
EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST         = 'smtp.gmail.com'
EMAIL_PORT         = 587
EMAIL_USE_TLS      = True
EMAIL_HOST_USER    = 'circular@bietdvg.edu'
EMAIL_HOST_PASSWORD= 'nzdj iedd gjry ovet'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# 9. Gemini API key & configuration
# if DEBUG:
#     GOOGLE_API_KEY = 'DEMO-API-KEY'  # Replace with a fake or dummy value
# else:
#     GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", 'REAL-KEY-HERE')  # use actual in prod

# genai.configure(api_key=GOOGLE_API_KEY)

# ─────────────────────────────────────────────────────────────────────────────
# 9. Gemini API key & configuration
# ─────────────────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = 'AIzaSyBstaypNftg37NdkYIz1ZN63m_u87xXisI'

# configure generative AI client at startup
genai.configure(api_key=GOOGLE_API_KEY)

# ─────────────────────────────────────────────────────────────────────────────
# 10. Auth redirects
# ─────────────────────────────────────────────────────────────────────────────
LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/'
