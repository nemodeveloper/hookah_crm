from django.core.management import BaseCommand

from src.apps.cashbox.models import MoneyType, CashBox


class Command(BaseCommand):

    def handle(self, *args, **options):
        cash_boxs = []
        print('Start create cashboxs task...')
        for box_type in MoneyType:
            print('Create cashbox with type %s' % box_type[0])
            cash_boxs.append(CashBox(cash_type=box_type[0], cash=0))
        CashBox.objects.bulk_create(cash_boxs)
        print('Success finish create moneybox task')

