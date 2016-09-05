
from src.apps.cashbox.models import ProductSell
from src.apps.ext_user.models import ExtUser, WorkProfile
from src.common_helper import date_to_verbose_format


class ProductSellEmployerReportProcessor(object):

    class ProductSellReport(object):

        def __init__(self, product_sell, percent):
            self.product_sell = product_sell
            self.percent = percent

        def get_sell(self):
            return self.product_sell

        def get_sell_employer_amount(self):
            return float(self.product_sell.get_sell_amount()) / 100 * self.percent

    def __init__(self, user_id, start_date, end_date):
        super(ProductSellEmployerReportProcessor, self).__init__()

        self.start_date = start_date
        self.end_date = end_date
        self.user = ExtUser.objects.get(id=user_id)
        self.is_admin = False
        self.product_sell_report = []
        self.total_employer_percent_amount = 0
        self.__process()

    def __process(self):
        profile = WorkProfile.objects.filter(ext_user=self.user).first()
        if not profile:
            self.is_admin = True
            return

        product_sells = ProductSell.objects\
            .filter(seller=self.user)\
            .filter(sell_date__range=(self.start_date, self.end_date))\
            .order_by('sell_date')
        if product_sells:
            for sell in product_sells:
                sell_report = self.ProductSellReport(sell, profile.percent_per_sale)
                self.product_sell_report.append(sell_report)
                self.total_employer_percent_amount += sell_report.get_sell_employer_amount()
            self.total_employer_percent_amount = '%.2f' % self.total_employer_percent_amount

    def __str__(self):
        return "Продажи за период с %s по %s" % (date_to_verbose_format(self.start_date), date_to_verbose_format(self.end_date))
