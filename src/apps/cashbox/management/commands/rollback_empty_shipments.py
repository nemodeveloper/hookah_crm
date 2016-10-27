from django.core.management import BaseCommand
from django.db import transaction

from src.apps.cashbox.models import ProductShipment, ProductSell
from src.apps.storage.service import update_product_storage, UPDATE_STORAGE_INC_TYPE


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Start rollback_empty_shipments task...')

        shipments = ProductShipment.objects.all()
        empty_product_shipments = []
        for shipment in shipments:
            if not ProductSell.objects.filter(shipments__id=shipment.id).first():
                empty_product_shipments.append(shipment)

        with transaction.atomic():
            if empty_product_shipments:
                for shipment in empty_product_shipments:
                    print('Начинаем возврат товара - %s на склад...' % str(shipment))
                    update_product_storage(shipment.product, UPDATE_STORAGE_INC_TYPE, shipment.product_count)
                    shipment.delete()

        print('Success finish rollback_empty_shipments task...')
