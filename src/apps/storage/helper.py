
class FakeProductStorage(object):

    def __init__(self, business_product, **kwargs):
        self.id = business_product.id
        self.product_name = business_product.product_name
        self.cost_price = str(business_product.cost_price)
        self.price_retail = str(business_product.price_retail)
        self.price_discount = str(business_product.price_discount)
        self.price_wholesale = str(business_product.price_wholesale)
        self.product_count = kwargs.get('product_count')
