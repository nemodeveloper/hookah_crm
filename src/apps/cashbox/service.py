from django.db import transaction

from src.apps.cashbox.serializer import FakeProductShipment, FakePaymentType
from src.apps.cashbox.models import ProductShipment, PaymentType, CashBox, ProductSell
from src.apps.storage.models import ProductStorage
from src.common_helper import build_json_from_dict


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


def update_cashbox_by_cash_take(cash_take):

    cashbox = CashBox.objects.get(cash_type=cash_take.cash_type)
    cashbox.cash -= cash_take.cash
    cashbox.save()


class RollBackSellProcessor(object):

    @staticmethod
    def rollback_shipment(shipment):
        product = ProductStorage.objects.get(pk=shipment.product.id)
        product.product_count += shipment.product_count
        product.save()

    @staticmethod
    def rollback_sell(sell_id):

        sell = ProductSell.objects.get(id=sell_id)
        with transaction.atomic():
            shipments = sell.shipments.all()
            for shipment in shipments:
                RollBackSellProcessor.rollback_shipment(shipment)
            sell.shipments.remove()

            payments = sell.payments.all()
            for payment in payments:
                cashbox = CashBox.objects.get(cash_type=payment.cash_type)
                cashbox.cash -= payment.cash
                cashbox.save()
            sell.payments.remove()
            sell.delete()

    @staticmethod
    def rollback_raw_sell(payments, shipments):

        with transaction.atomic():
            if shipments:
                shipment_entities = ProductShipment.objects.filter(pk__in=shipments)
                for shipment in shipment_entities:
                    RollBackSellProcessor.rollback_shipment(shipment)
                shipment_entities.delete()

            if payments:
                payment_entities = PaymentType.objects.filter(pk__in=payments)
                payment_entities.remove()
