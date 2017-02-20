# -*- coding: utf-8 -*-

DEBUG = False


DATABASE_NAME = 'hookahcrm_db'
DATABASE_ENGINE = 'postgresql_psycopg2'
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
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': 'hookahcrm',
        'PASSWORD': '1234',
        'HOST': '127.0.0.1',
        'PORT': '',
        'CONN_MAX_AGE': 60,
    }
}
