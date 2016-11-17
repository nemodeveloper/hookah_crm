from .settings import *


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

LOGGING['loggers']['django.db.backends'] = {
            'level': 'DEBUG',
            'handlers': ['console_sql'],
            'propagate': False,
}
