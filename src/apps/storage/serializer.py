

class FakeProduct(object):

    def __init__(self, product, **kwargs):
        self.id = product.id
        self.product_group = kwargs['product_group']
        self.product_category = kwargs['product_category']
        self.product_kind = kwargs['product_kind']
        self.product_name = product.product_name
        self.cost_price = str(product.cost_price)
        self.price_retail = str(product.price_retail)
        self.price_discount = str(product.price_discount)
        self.price_opt_1 = str(product.price_opt_1)
        self.price_opt_2 = str(product.price_opt_2)
        self.price_opt_3 = str(product.price_opt_3)
        self.product_count = product.product_count


class FakeProductKind(object):

    def __init__(self, kind, **kwargs):
        self.id = kind.id
        self.kind_name = kind.kind_name
        self.category = kwargs.get('category')
        self.group = kwargs.get('group')
