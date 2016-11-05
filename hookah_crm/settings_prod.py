from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'hookahcrm.pythonanywhere.com'
]

DATABASE_NAME = 'hookahcrm$default'
DATABASE_ENGINE = 'mysql'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': 'hookahcrm',
        'PASSWORD': 'dsytujnjds1',
        'HOST': 'hookahcrm.mysql.pythonanywhere-services.com',
        'PORT': '',
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'sql_mode': 'TRADITIONAL',
            'charset': 'utf8',
            'init_command': 'SET '
                'storage_engine=INNODB,'
                'character_set_connection=utf8,'
                'collation_connection=utf8_bin'
        }
    }
}
