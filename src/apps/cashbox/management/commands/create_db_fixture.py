import os

from django.core.management import BaseCommand, call_command
from django.core.management.commands import dumpdata
from django.utils import timezone

from hookah_crm import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Start dump_data task...')

        fixture_file = os.path.join(settings.BASE_DIR, 'database\db_fixture_%s.json' % timezone.now().strftime('%Y_%m_%d_%H_%M'))
        params = {
            'app_label': 'all',
            'use_natural_foreign_keys': True,
            'use_natural_primary_keys': True,
            'indent': 4,
            'output': fixture_file,
            'verbosity': 0
        }

        call_command(dumpdata.Command(), **params)
        print('Success finish dump_date task!')
