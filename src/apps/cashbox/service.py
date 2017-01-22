import logging

from django.db import transaction

from src.apps.cashbox.serializer import FakeProductShipment, FakePaymentType
from src.apps.cashbox.models import ProductShipment, PaymentType, CashBox, ProductSell
from src.apps.storage.models import Product
from src.common_helper import build_json_from_dict


cashbox_log = logging.getLogger('cashbox_log')


def get_product_shipment_json(id):

    shipment = ProductShipment.objects.get(id=id)
    return build_json_from_dict(FakeProductShipment(shipment))


def get_payment_type_json(id):

    payment_type = PaymentType.objects.get(id=id)
    return build_json_from_dict(FakePaymentType(payment_type))


def update_cashbox_by_payments(payments):

    for payment in payments:
        cashbox = CashBox.objects.get(cash_type=payment.cash_type)
        cashbox.cash += payment.cash
        cashbox.save()


class RollBackSellProcessor(object):

    @staticmethod
    def rollback_sell(sell_id):

        sell = ProductSell.objects.select_related('seller').prefetch_related('shipments', 'payments').get(id=sell_id)
        cashbox_log.info('Инициирован откат продажи[id=%s] - %s' % (sell_id, sell.get_log_info()))
        with transaction.atomic():
            shipments = sell.shipments.select_related('product').all()
            for shipment in shipments:
                cashbox_log.info('Инициирован откат партии товара из продажи[id=%s] - %s' % (sell_id, shipment))
                shipment.roll_back_product_to_storage()
            sell.shipments.remove()

            payments = sell.payments.all()
            for payment in payments:
                cashbox_log.info('Инициирован откат оплаты из продажи[id=%s] - %s' % (sell_id, payment))
                payment.rollback_from_cashbox()
            sell.payments.remove()
            sell.delete()
            cashbox_log.info('Откат продажи[id=%s] завершен!' % sell_id)

    @staticmethod
    def rollback_raw_sell(payments, shipments):

        with transaction.atomic():
            if shipments:
                shipment_entities = ProductShipment.objects.select_related().filter(pk__in=shipments)
                for shipment in shipment_entities:
                    shipment.roll_back_product_to_storage()
                shipment_entities.delete()

            if payments:
                payment_entities = PaymentType.objects.filter(pk__in=payments)
                payment_entities.delete()
