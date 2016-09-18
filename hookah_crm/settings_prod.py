from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'hookahcrm.pythonanywhere.com'
]

DATABASE_NAME = 'hookahcrm$nemodev'
DATABASE_ENGINE = 'mysql'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': 'hookahcrm',
        'PASSWORD': 'dsytujnjds1',
        'HOST': 'hookahcrm.mysql.pythonanywhere-services.com',
        'PORT': '',
    }
}
