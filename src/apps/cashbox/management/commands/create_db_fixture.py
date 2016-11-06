from django.core.management import BaseCommand

from src.schedulers.schedulers import create_db_fixture


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Start create_db_fixture task...')
        create_db_fixture()
        print('Success finish create_db_fixture task!')
