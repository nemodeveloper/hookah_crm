# -*- coding: utf-8 -*-
import os
import sys

# explicitly set package path
path = '/home/hookahcrm/hookah_crm/'
if path not in sys.path:
    sys.path.append(path)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'hookah_crm.settings_prod'

from src.schedulers.schedulers import create_db_fixture


def start_create_db_fixture_task():
    create_db_fixture()


start_create_db_fixture_task()

