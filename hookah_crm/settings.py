import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'lfpeddg3xx-a2c*=c5$u8=+^d&#lk8a3-oricyrtalie+!)@uo'

DEBUG = True

ALLOWED_HOSTS = []

WSGI_APPLICATION = 'hookah_crm.wsgi.application'

AUTH_USER_MODEL = 'ext_user.ExtUser'

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
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APP + PROJECT_APPS


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = 'hookah_crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


# database
DATABASE_NAME = 'dev_db.sqlite3'
DATABASE_ENGINE = 'sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
        'NAME': os.path.join(BASE_DIR, 'database/%s' % DATABASE_NAME),
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

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = False
USE_TZ = True


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

