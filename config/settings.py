
"""
Django settings for the FanFlow project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables from .env
# Render environment variables will also be available through os.environ.
load_dotenv(BASE_DIR / '.env')


def env_bool(key, default=False):
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ('1', 'true', 'yes', 'on')


# Security settings
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-fallback-key-change-me'
)

DEBUG = env_bool('DEBUG', True)

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

if not DEBUG:
    ALLOWED_HOSTS += [
        host.strip()
        for host in os.getenv('ALLOWED_HOSTS', '').split(',')
        if host.strip()
    ]


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
]

LOCAL_APPS = [
    'accounts',
    'dashboard',
    'products',
    'materials',
    'inventory',
    'suppliers',
    'orders',
    'production',
    'forecasting',
    'procurement',
    'logistics',
    'analytics',
    'risk_management',
    'ai_assistant',
    'notifications',
    'reports',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.sidebar_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# SQLite is used by default for local development.
# For PostgreSQL, set DB_ENGINE=postgres and configure the DB variables.

if os.getenv('DB_ENGINE', 'sqlite').lower() == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator'
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise compressed static files
STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Production security
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

    CSRF_TRUSTED_ORIGINS = [
        origin.strip()
        for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
        if origin.strip()
    ]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Login/logout redirects
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'accounts:login'


# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# LLM / AI Assistant configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')


# ML model and dataset storage locations
ML_MODELS_DIR = BASE_DIR / 'ml_models'
DATASETS_DIR = BASE_DIR / 'datasets'
