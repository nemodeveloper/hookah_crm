from django.core.management import BaseCommand
from django.db import transaction

from src.apps.cashbox.models import ProductShipment, ProductSell


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Start rollback_empty_shipments task...')

        shipments = ProductShipment.objects.select_related('product').all()
        empty_product_shipments = []
        for shipment in shipments:
            if not ProductSell.objects.filter(shipments__id=shipment.id).first():
                empty_product_shipments.append(shipment)

        with transaction.atomic():
            if empty_product_shipments:
                for shipment in empty_product_shipments:
                    shipment.delete()

        print('Success finish rollback_empty_shipments task...')
