from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'hookahcrm.pythonanywhere.com'
]

DATABASE_NAME = 'nemodev_hookahcrm_db.sqlite3'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DATABASE_ENGINE,
        'NAME': os.path.join(BASE_DIR, 'database/%s' % DATABASE_NAME),
    }
}
