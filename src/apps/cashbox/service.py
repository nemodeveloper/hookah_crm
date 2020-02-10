import logging

from django.db import transaction

from src.apps.cashbox import utils
from src.apps.cashbox.serializer import FakeProductShipment, FakePaymentType
from src.apps.cashbox.models import ProductShipment, PaymentType, ProductSell
from src.apps.storage.models import Product
from src.common_helper import build_json_from_dict


cashbox_log = logging.getLogger('cashbox_log')


def get_product_shipment_json(id):

    shipment = ProductShipment.objects.get(id=id)
    return build_json_from_dict(FakeProductShipment(shipment))


def get_payment_type_json(id):

    payment_type = PaymentType.objects.get(id=id)
    return build_json_from_dict(FakePaymentType(payment_type))


class RollBackSellProcessor(utils.ProductSellRestrictionMixin):

    def rollback_sell(self, sell_id):

        with transaction.atomic():
            sell = ProductSell.objects.select_for_update(nowait=True).select_related('seller').get(id=sell_id)
            self.check_sell_owner(sell)
            cashbox_log.info('Инициирован откат продажи[id=%s] - %s' % (sell_id, sell.get_log_info()))

            shipments = sell.get_shipments()
            for shipment in shipments:
                cashbox_log.info('Инициирован откат партии товара из продажи[id=%s] - %s' % (sell_id, shipment))
                shipment.roll_back_product_to_storage()
            sell.delete()
            cashbox_log.info('Откат продажи[id=%s] завершен!' % sell_id)

    def rollback_raw_sell(self, payments, shipments):

        with transaction.atomic():
            if shipments:
                ProductShipment.objects.filter(pk__in=shipments).delete()

            if payments:
                PaymentType.objects.filter(pk__in=payments).delete()
