from .settings import *

# отладка
DEBUG_APPS = [
    'debug_toolbar'
]

# INSTALLED_APPS += DEBUG_APPS

# MIDDLEWARE = [
#     'debug_toolbar.middleware.DebugToolbarMiddleware'
# ] + MIDDLEWARE

# Start debug-toolbar definition

INTERNAL_IPS = ['127.0.0.1']
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

# End debug-toolbar definition

# templates
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
            'builtins': [
                'src.template_tags.common_tags',
            ],
        },
    },
]

# loggers
LOGGING['loggers'] = {
    'django.db.backends': {
        'level': 'DEBUG',
        'handlers': ['console_sql'],
        'propagate': False,
    },
    'common_log': {
        'handlers': ['common_file', 'console'],
        'level': 'INFO',
        'propagate': False,
    },
    'cashbox_log': {
        'handlers': ['cashbox_file', 'console'],
        'level': 'INFO',
        'propagate': False,
    },
    'storage_log': {
        'handlers': ['storage_file', 'console'],
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
        'handlers': ['common_file', 'console'],
        'propagate': True,
    },
    'django.request': {
        'handlers': ['common_file', 'console'],
        'level': 'WARNING',
        'propagate': True,
    },
    '': {
        'level': 'WARNING',
        'handlers': ['common_file', 'console'],
        'propagate': True,
    }
}

DATABASE_NAME = 'dev_hookahcrm_db'
DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': 'dev_hookahcrm',
        'PASSWORD': '1234',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,
    }
}
