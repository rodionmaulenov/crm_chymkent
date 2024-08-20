"""
Django settings for crm_kazakhstan project.

Generated by 'django-admin startproject' using Django 3.2.23.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
from decouple import config
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG')

ALLOWED_HOSTS = [config('ALLOWED_HOSTS')]

AUTH_USER_MODEL = 'gmail_messages.CustomUser'

# Application definition

INSTALLED_APPS = [
    # django-admin theme
    "admin_interface",
    "colorfield",

    # basic django application
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party packages
    'django_celery_beat',
    'debug_toolbar',
    'guardian',
    'rangefilter',

    # MY APPS
    'mothers',
    'ban',
    'gmail_messages',
    # many-to-one relationships with mother
    'documents',
]

# setup django-admin theme
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # switch languages
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'crm_kazakhstan.middleware.TimezoneMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# for django-debug-toolbar
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

ROOT_URLCONF = 'crm_kazakhstan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'crm_kazakhstan', 'templates')],
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

WSGI_APPLICATION = 'crm_kazakhstan.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'NAME': config('SQL_NAME'),
        'USER': config('SQL_USER'),
        'PASSWORD': config('SQL_PASSWORD'),
        # 'HOST': config('SQL_HOST'),
        'HOST': 'localhost',
        'PORT': config('SQL_PORT'),
    }
}

CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# CELERY BEAT SCHEDULER
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CELERY_BEAT_SCHEDULE = {
    'delete_weekday_objects': {
        'task': 'mothers.tasks.delete_weekday_objects',
        'schedule': crontab(hour='0', minute='0', day_of_week='monday'),  # Every Monday at midnight
    },
    'delete_weekend_objects': {
        'task': 'mothers.tasks.delete_weekend_objects',
        'schedule': crontab(hour='0', minute='0', day_of_week='saturday'),  # Every Saturday at midnight
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django-guardian for Object Level Permission on admin
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,  # Disable all existing loggers
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'custom_logger': {  # Define a custom logger
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,  # Do not propagate to other loggers
        },
    },
}
