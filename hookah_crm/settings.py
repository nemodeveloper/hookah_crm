# -*- coding: utf-8 -*-
import os
from django.conf.global_settings import gettext_noop
from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'lfpeddg3xx-a2c*=c5$u8=+^d&#lk8a3-oricyrtalie+!)@uo'

DEBUG = bool(os.environ.get('DEBUG', 'True'))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# main settings
WSGI_APPLICATION = 'hookah_crm.wsgi.application'
ROOT_URLCONF = 'hookah_crm.urls'

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

EXTERNAL_APP = []

PROJECT_APPS = [
    'src.apps.storage.apps.StorageConfig',
    'src.apps.ext_user.apps.ExtUserConfig',
    'src.apps.cashbox.apps.CashBoxConfig',
    'src.apps.csa.apps.CSAConfig',
    'src.apps.market.apps.MarketConfig',
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APP + PROJECT_APPS

# settings BACKENDS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 11 * 60 * 60       # 11 часов

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# middleware
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'src.base_components.middleware.request.RequestMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'src.template_tags.common_tags',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ])
            ]
        },
    },
]

# End debug-toolbar definition

# database
DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.environ.get('DATABASE_PORT', '5432')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'dev_hookah')
DATABASE_USER = os.environ.get('DATABASE_USER', 'dev_hookah')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', '1234')
DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
        'CONN_MAX_AGE': 60 * 10,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },

    'formatters': {
        'verbose': {
            'format': u'[%(levelname)s] [%(asctime)s] [%(module)s] [%(process)d] [%(thread)d] [%(message)s]',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
        'simple': {
            'format': u'[%(levelname)s] [%(message)s]'
        },
        'sql': {
            'format': u'[%(levelname)s] [%(asctime)s]\n[sql_text=%(sql)s]\n[sql_params=%(params)s]',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'console_sql': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'sql',
            'filters': ['require_debug_true'],
        },
        'common_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 30,
            'encoding': 'utf-8',
            'filename': os.path.join(BASE_DIR, 'logs/common.log'),
            'formatter': 'verbose',
            'filters': [],
        },
        'cashbox_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 30,
            'encoding': 'utf-8',
            'filename': os.path.join(BASE_DIR, 'logs/cashbox.log'),
            'formatter': 'verbose',
            'filters': [],
        },
        'storage_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 30,
            'encoding': 'utf-8',
            'filename': os.path.join(BASE_DIR, 'logs/storage.log'),
            'formatter': 'verbose',
            'filters': [],
        },
        'storage_product_count_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 30,
            'encoding': 'utf-8',
            'filename': os.path.join(BASE_DIR, 'logs/storage_product_count.log'),
            'formatter': 'verbose',
            'filters': [],
        },
    },
    'loggers': {
        'django.db.backends': {
                'level': os.environ.get('DATABASE_LOG_LEVEL', 'WARNING'),
                'handlers': ['console_sql'],
                'propagate': False,
            },
        'common_log': {
            'handlers': ['common_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'cashbox_log': {
            'handlers': ['cashbox_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'storage_log': {
            'handlers': ['storage_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'storage_product_count_log': {
            'handlers': ['storage_product_count_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'level': 'WARNING',
            'handlers': ['common_file'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['common_file'],
            'level': 'WARNING',
            'propagate': True,
        },
        '': {
            'level': 'WARNING',
            'handlers': ['common_file'],
            'propagate': True,
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'ru'
LANGUAGES = (
    ('ru', _('Russian')),
)
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = False
USE_TZ = False

DATE_FORMAT = '%d.%m.%Y %H:%M'
SHORT_DATE_FORMAT = '%d.%m.%Y'

CLIENT_DATE_FORMAT = '%Y-%m-%dT%H:%M'
CLIENT_SHORT_DATE_FORMAT = '%Y-%m-%d'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

# static - место куда будет складываться статика коммандой collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'files', 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'files', 'media')
MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = 'media/admin'

# место для статики
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'templates/src/'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# upload files config
FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, 'temp')
FILE_UPLOAD_HANDLERS = [
    "django_excel.ExcelMemoryFileUploadHandler",
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django_excel.TemporaryExcelFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler"
]

# CSA
LOGIN_URL = '/csa/login/'
LOGOUT_URL = '/csa/logout/'
AUTH_USER_MODEL = 'ext_user.ExtUser'
