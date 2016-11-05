from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'hookahcrm.pythonanywhere.com'
]

DATABASE_NAME = 'hookahcrm$nemodev'
DATABASE_ENGINE = 'mysql'
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
    #     'NAME': DATABASE_NAME,
    #     'USER': 'hookahcrm',
    #     'PASSWORD': 'dsytujnjds1',
    #     'HOST': 'hookahcrm.mysql.pythonanywhere-services.com',
    #     'PORT': '',
    #     'CONN_MAX_AGE': 60,
    #     'OPTIONS': {
    #         'sql_mode': 'TRADITIONAL',
    #         'charset': 'utf8',
    #         'init_command': 'SET '
    #             'storage_engine=INNODB,'
    #             'character_set_connection=utf8,'
    #             'collation_connection=utf8_bin'
    #     }
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'nemodev_hookahcrm',
        'USER': 'yournewuser',
        'PASSWORD': 'dsytujnjds1',
        'HOST': 'hookahcrm-253.postgres.pythonanywhere-services.com',
        'PORT': '10253',
        'CONN_MAX_AGE': 60,
    }
}
