from src.apps.cashbox.helper import FakeProductShipment, FakePaymentType
from src.apps.cashbox.models import ProductShipment, PaymentType, CashBox
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
