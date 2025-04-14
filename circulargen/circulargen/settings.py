from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-…'
DEBUG = True
ALLOWED_HOSTS = []

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
    'generator.middleware.LoginRequiredMiddleware',   # your custom middleware

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'circulargen.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'generator' / 'templates'],  # Add this
        # 'DIRS': [ BASE_DIR / 'templates' ],   # ← add this

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'static' ]  # For development (optional but useful)
STATIC_ROOT = BASE_DIR / 'staticfiles'      # For collectstatic to gather all into this dir
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'circulargen', 'static'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SMTP Email settings
EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST         = 'smtp.gmail.com'
EMAIL_PORT         = 587
EMAIL_HOST_USER    = 'adarshn54688@gmail.com'
EMAIL_HOST_PASSWORD= 'cqyd cqye jdri ayyq'
EMAIL_USE_TLS      = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Gemini API key (hard‑coded here, but you can switch to os.environ)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBcz6ihq-BM64VgiS8O_g5PJiNrmE9-JL8")

# Login URLs
LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/'
