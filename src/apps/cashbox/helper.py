

class FakeProductShipment(object):

    def __init__(self, bus_object, **kwargs):
        self.id = bus_object.id
        product = bus_object.product
        self.product_name = product.product_name
        self.product_category = product.product_category.category_name
        self.product_kind = product.product_kind.kind_name
        self.product_count = bus_object.product_count
        self.cost_price = str(bus_object.cost_price)


class FakePaymentType(object):

    def __init__(self, bus_object, **kwargs):
        self.id = bus_object.id
        self.cash_type = bus_object.get_cash_type_display()
        self.cash = str(bus_object.cash)
        self.description = bus_object.description
