from src.apps.storage.models import Product


class FakeProductShipment(object):

    def __init__(self, bus_object):
        self.id = bus_object.id
        product = Product.objects.select_related().get(id=bus_object.product_id)
        product_kind = product.product_kind
        self.product_id = product.id
        self.product_group = product_kind.product_category.product_group.group_name
        self.product_category = product_kind.product_category.category_name
        self.product_kind = product_kind.kind_name
        self.product_name = product.product_name
        self.product_count = bus_object.product_count
        self.storage_product_count = product.product_count
        self.cost_price = str(bus_object.cost_price)


class FakePaymentType(object):

    def __init__(self, bus_object):
        self.id = bus_object.id
        self.cash_type = bus_object.get_cash_type_display()
        self.cash = str(bus_object.cash)
        self.description = bus_object.description
