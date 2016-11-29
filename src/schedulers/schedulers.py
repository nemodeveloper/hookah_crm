# -*- coding: utf-8 -*-

import logging
import os

from django.core.management import call_command
from django.core.management.commands import dumpdata
from django.utils import timezone

from hookah_crm import settings


logger = logging.getLogger('common_log')


def create_db_fixture():
    fixture_file = os.path.join(settings.BASE_DIR,
                                'database/db_fixture_%s.json' % timezone.now().strftime('%Y_%m_%d_%H_%M'))
    logger.info(u'Начинаем создание резервной копии бд....')
    params = {
        'app_label': 'all',
        'use_natural_foreign_keys': True,
        'use_natural_primary_keys': True,
        'indent': 4,
        'output': fixture_file,
        'verbosity': 0
    }
    call_command(dumpdata.Command(), **params)
    logger.info(u'Успешное создание резервной копии бд....')

    return fixture_file
