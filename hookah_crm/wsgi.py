import os
import sys

from django.core.wsgi import get_wsgi_application

from hookah_crm.settings import DEBUG


path = os.environ.get('APP_HOME', '/home/app/web/') + 'hookah_crm'
if path not in sys.path:
    sys.path.append(path)


os.environ['DJANGO_SETTINGS_MODULE'] = 'hookah_crm.settings'

if not DEBUG:
    from django.contrib.staticfiles.handlers import StaticFilesHandler
    application = StaticFilesHandler(get_wsgi_application())
else:
    application = get_wsgi_application()
