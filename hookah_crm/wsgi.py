import os
import sys

from django.core.wsgi import get_wsgi_application

path = '/home/hookah/hookah_crm'
if path not in sys.path:
    sys.path.append(path)

from hookah_crm.settings_helper import *
os.environ['DJANGO_SETTINGS_MODULE'] = SETTINGS_MODULE

if PRODUCTION:
    from whitenoise.django import DjangoWhiteNoise
    application = DjangoWhiteNoise(get_wsgi_application())
else:
    application = get_wsgi_application()