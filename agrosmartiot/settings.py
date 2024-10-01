"""
Django settings for agrosmartiot project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path
import django_heroku
import pytz
AUTH_USER_MODEL = 'agrosmartiotweb.CustomUser'
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-i+h^ifkudr)+q*__he#@n=#=q*rk17-b!3^ns4vmt+5og7sqz1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# settings.py

LOGIN_FORM = 'agrosmartiotweb.forms.CustomLoginForm'
LOGIN_URL = 'login'
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'agrosmartiotweb', 'agrosmartiot',
    'django.contrib.humanize', 'crispy_forms', "django_filters", "rest_framework", "import_export", "mptt"
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

ROOT_URLCONF = 'agrosmartiot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Cambia a 'templates' en lugar de 'templates/agrosmart'
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'agrosmartiotweb.context_processors.empresa_info',
            ],
        },
    },
]


WSGI_APPLICATION = 'agrosmartiot.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

import dj_database_url
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),  # Ubicación del archivo de la base de datos
    }
}
# settings.py
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Kafka
KAFKA_SERVER = 'localhost:9092'
KAFKA_TOPIC = 'temperatura-topic'

# Django Heroku settings

SESSION_COOKIE_SECURE = False  # Si no estás usando HTTPS, asegúrate de que esto sea False
CSRF_COOKIE_SECURE = False     # Asegúrate de que sea False en desarrollo
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

ALLOWED_HOSTS = [
    'web-production-3711.up.railway.app',
    'localhost',
    '127.0.0.1',  # Agrega esto
]

