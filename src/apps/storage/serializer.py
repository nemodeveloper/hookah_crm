

class FakeProductStorage(object):

    def __init__(self, business_product, **kwargs):
        self.id = business_product.id
        self.product_name = business_product.product_name
        self.cost_price = str(business_product.cost_price)
        self.price_retail = str(business_product.price_retail)
        self.price_discount = str(business_product.price_discount)
        self.price_wholesale = str(business_product.price_wholesale)
        self.price_shop = str(business_product.price_shop)
        self.product_count = kwargs.get('product_count')


class FakeProductKind(object):

    def __init__(self, kind, **kwargs):
        self.id = kind.id
        self.kind_name = kind.kind_name
        self.category = kwargs.get('category')
        self.group = kwargs.get('group')
