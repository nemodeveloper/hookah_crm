import operator
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q

from hookah_crm import settings
from src.apps.cashbox.models import ProductSell
from src.apps.ext_user.models import ExtUser, WorkProfile
from src.apps.storage.models import Product
from src.base_components.middleware import request
from src.common_helper import date_to_verbose_format
from src.template_tags.common_tags import format_date, round_number

PERIOD_KEY = 'period_type'
DAY_PERIOD_KEY = 'day'
MONTH_PERIOD_KEY = 'month'
CUSTOM_PERIOD_KEY = 'period'


def get_period(period_type, period_start, period_end):
    start_date = datetime.now()
    end_date = datetime.now()

    if DAY_PERIOD_KEY == period_type:
        pass
    elif MONTH_PERIOD_KEY == period_type:
        start_date = datetime.now() + relativedelta(day=1)
        end_date = datetime.now() + relativedelta(day=1, months=+1, days=-1)
    elif CUSTOM_PERIOD_KEY == period_type:
        start_date = datetime.strptime(period_start, settings.CLIENT_SHORT_DATE_FORMAT)
        end_date = datetime.strptime(period_end, settings.CLIENT_SHORT_DATE_FORMAT)

    start_date = start_date.replace(hour=0, minute=0, second=0)
    end_date = end_date.replace(hour=23, minute=59, second=59)

    return start_date, end_date


class ReportEmployerForPeriodProcessor(object):

    class ProductSellReport(object):

        def __init__(self, product_sell, percent):
            self.product_sell = product_sell
            self.percent = percent

        def get_sell_employer_amount(self):
            return self.product_sell.get_sell_amount() / 100 * self.percent

    class WorkSessionReport(object):

        def __init__(self, work_session, amount_for_hour):
            super(ReportEmployerForPeriodProcessor.WorkSessionReport, self).__init__()
            self.session = work_session
            self.amount_for_hour = amount_for_hour

        def get_work_session_amount(self):
                return float(self.session.get_work_hours()) * float(self.amount_for_hour)

    def __init__(self, user_id, start_date, end_date):
        super(ReportEmployerForPeriodProcessor, self).__init__()

        self.start_date = start_date
        self.end_date = end_date
        self.user = ExtUser.objects.get(id=user_id)
        self.is_admin = False
        self.product_sells = []
        self.work_sessions = []
        self.total_employer_percent_amount = 0
        self.total_employer_work_time_amount = 0
        self.total_amount = 0
        self.money_per_hour = 0
        self.percent_per_sale = 0
        self.__process()

    def __process(self):
        profile = WorkProfile.objects.filter(ext_user=self.user).first()
        if not profile:
            self.is_admin = True
            return

        product_sells = ProductSell.objects\
            .filter(seller=self.user)\
            .filter(sell_date__range=(self.start_date, self.end_date))\
            .order_by('-sell_date')
        if product_sells:
            for sell in product_sells:
                sell_report = self.ProductSellReport(sell, profile.percent_per_sale)
                self.product_sells.append(sell_report)
                self.total_employer_percent_amount += sell_report.get_sell_employer_amount()

        # отключаем расчет рабочего времени
        # work_sessions = WorkSession.objects\
        #     .filter(ext_user=self.user)\
        #     .filter(start_workday__range=(self.start_date, self.end_date))\
        #     .order_by('start_workday')
        #
        # if work_sessions:
        #     for session in work_sessions:
        #         work_session = self.WorkSessionReport(session, profile.money_per_hour)
        #         self.work_sessions.append(work_session)
        #         self.total_employer_work_time_amount += work_session.get_work_session_amount()

        # self.total_amount = self.total_employer_work_time_amount + self.total_employer_percent_amount
        # self.money_per_hour = str(profile.money_per_hour)
        self.percent_per_sale = profile.percent_per_sale

    def __str__(self):
        return "Продажи за период с %s по %s" % (date_to_verbose_format(self.start_date), date_to_verbose_format(self.end_date))


class ProductSellReportForPeriod(object):

    def __init__(self, start_date, end_date, customer_ids):
        super(ProductSellReportForPeriod, self).__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.customer_ids = customer_ids
        self.user = request.get_current_user()
        self.sells = []
        self.total_amount = 0
        self.total_rebate_amount = 0
        self.payments = {}

    def get_sells(self):
        date_criteria = Q(sell_date__range=(self.start_date, self.end_date))
        customer_criteria = Q()
        user_criteria = Q()

        if self.customer_ids:
            customer_criteria = Q(customer_id__in=self.customer_ids)

        if not self.user.is_superuser:
            user_criteria = Q(seller_id=self.user.id)

        sell_query = ProductSell.objects \
            .select_related('customer__customer_type') \
            .filter(date_criteria & user_criteria & customer_criteria) \
            .order_by('-sell_date')

        return sell_query

    def process(self):
        self.sells = self.get_sells()

        for sell in self.sells:
            self.total_amount += sell.get_sell_amount()
            self.total_rebate_amount += sell.get_rebate_amount()
            self.__process_payments(sell.get_payments())

        return self

    def __process_payments(self, payments):
        for payment in payments:
            if not self.payments.get(payment.get_cash_type_display()):
                self.payments[payment.get_cash_type_display()] = 0
            self.payments[payment.get_cash_type_display()] += round_number(payment.cash, 2)

    def __str__(self):
        return 'Список продаж товара с %s по %s' % (format_date(self.start_date), format_date(self.end_date))


class ProductSellCreditReport(object):

    def __init__(self, start_date, end_date):
        super(ProductSellCreditReport, self).__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.sells = []
        self.credit_amount = 0

    def process(self):
        self.sells = ProductSell.objects.prefetch_related('payments').select_related().\
            filter(payments__cash_type='CREDIT').\
            filter(sell_date__range=(self.start_date, self.end_date)).\
            order_by('-sell_date')
        for sell in self.sells:
            self.credit_amount += sell.get_credit_payment_amount()

        return self

    def __str__(self):
        return 'Список должников с %s по %s' % (format_date(self.start_date), format_date(self.end_date))


class ProductSellProfitReport(object):

    # Структура для аггрегирования товара
    class ProductAggr(object):

        def __init__(self, shipment):
            super(ProductSellProfitReport.ProductAggr, self).__init__()
            self.count = shipment.product_count                      # количество товаров
            self.product = shipment.product                          # товар
            self.cost_price = shipment.get_shipment_amount()         # фактическая стоимость
            self.product_cost = shipment.get_cost_amount()           # себестоимость

        def get_average_cost_price(self):
            return self.cost_price / self.count

        def get_average_product_cost(self):
            return self.product_cost / self.count

        def get_profit_amount(self):
            return self.cost_price - self.product_cost

        def aggregate(self, product_aggr):
            self.count += product_aggr.count
            self.cost_price += product_aggr.cost_price
            self.product_cost += product_aggr.product_cost

        def update_by_shipment(self, shipment):
            self.count += shipment.product_count
            self.cost_price += shipment.get_shipment_amount()
            self.product_cost += shipment.get_cost_amount()

        def to_kind_aggr(self):
            return ProductSellProfitReport.ProductKindAggr(self.product.product_kind)

    # Структура для аггрегирования статистики вида товара
    class ProductKindAggr(object):

        def __init__(self, kind):
            super(ProductSellProfitReport.ProductKindAggr, self).__init__()
            self.count = 0          # количество вида в одной продаже
            self.sell_cost = 0      # общая стоимость по цене в продаже
            self.product_cost = 0   # общая стоимость по себестоимости товара
            self.sell_count = 1     # будем считать в пределах одной продажи вид учавствовал 1 раз
            self.group = kind.product_category.product_group
            self.category = kind.product_category
            self.kind = kind
            self.products_aggr = []

        def get_average_sell_cost(self):
            return self.sell_cost / self.count

        def get_average_product_cost(self):
            return self.product_cost / self.count

        def get_profit_amount(self):
            return self.sell_cost - self.product_cost

        def update(self, product_kind_aggr):
            self.count += product_kind_aggr.count
            self.sell_cost += product_kind_aggr.sell_cost
            self.product_cost += product_kind_aggr.product_cost
            self.sell_count += 1

        def set_products(self, products):
            self.products_aggr = products

    class ProductCategoryAggr(object):

        def __init__(self, kind_aggr):
            super(ProductSellProfitReport.ProductCategoryAggr, self).__init__()
            self.sell_cost = 0                  # общая сумма с продаж по категориям
            self.group = kind_aggr.group        # группа товара с которой связана категория товара
            self.category = kind_aggr.category
            self.kinds_aggr = []
            self.profit_cost = 0
            self.add_kind_aggr(kind_aggr)

        def add_kind_aggr(self, kind_aggr):
            self.sell_cost += kind_aggr.sell_cost
            self.kinds_aggr.append(kind_aggr)
            self.profit_cost += kind_aggr.get_profit_amount()

    class ProductGroupAggr(object):

        def __init__(self, category_aggr):
            super(ProductSellProfitReport.ProductGroupAggr, self).__init__()
            self.sell_cost = 0              # общая сумма с продаж по группам
            self.group_name = category_aggr.group.group_name
            self.categories_aggr = []
            self.profit_cost = 0
            self.add_category_aggr(category_aggr)
            self.profit_percent = 0

        def add_category_aggr(self, category_aggr):
            self.sell_cost += category_aggr.sell_cost
            self.categories_aggr.append(category_aggr)
            self.profit_cost += category_aggr.profit_cost

    def __init__(self, start_date, end_date, sells=(), filtered_product_kind_ids=()):
        super(ProductSellProfitReport, self).__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.sells = sells
        self.filtered_product_kind_ids = filtered_product_kind_ids

        self.groups_aggr = {}
        self.categories_aggr = {}
        self.kinds_aggr = {}
        self.products_aggr = {}
        self.products_aggr_by_kind = {}

        self.total_cost_amount = 0
        self.total_profit_amount = 0
        self.total_percent = 0
        self.total_rebate_amount = 0

    # Получить агрегированные данные по товарам
    @staticmethod
    def get_sell_products_aggr(shipments):
        products_aggr = {}
        for shipment in shipments:
            cur_product = shipment.product
            cur_product_aggr = products_aggr.get(cur_product.id)
            if not cur_product_aggr:
                cur_product_aggr = ProductSellProfitReport.ProductAggr(shipment)
                products_aggr[cur_product.id] = cur_product_aggr
            else:
                cur_product_aggr.update_by_shipment(shipment)

        return products_aggr

    # Получить словарь агрегированных видов по продажам
    # Вида {kind_id: ProductKindAggr}
    @staticmethod
    def get_sell_kinds_aggr(shipments):
        kinds_aggr = {}
        for shipment in shipments:
            shipment_kind = shipment.product.product_kind
            cur_kind_aggr = kinds_aggr.get(shipment_kind.id)
            if not cur_kind_aggr:
                cur_kind_aggr = ProductSellProfitReport.ProductKindAggr(shipment_kind)
                kinds_aggr[shipment_kind.id] = cur_kind_aggr
            cur_kind_aggr.count += shipment.product_count
            cur_kind_aggr.sell_cost += shipment.get_shipment_amount()
            cur_kind_aggr.product_cost += shipment.get_cost_amount()

        return kinds_aggr

    def update_sell_products_aggr(self, products_aggr):
        for key, value in products_aggr.items():
            products_aggr = self.products_aggr.get(key)
            if not products_aggr:
                self.products_aggr[key] = value
            else:
                products_aggr.aggregate(value)

    def update_sell_kinds_aggr(self, kinds_aggr):
        for key, value in kinds_aggr.items():
            sell_kinds_aggr = self.kinds_aggr.get(key)
            if not sell_kinds_aggr:
                self.kinds_aggr[key] = value
            else:
                sell_kinds_aggr.update(value)

    def update_products_aggr(self):
        for product_aggr in self.products_aggr.values():
            cur_aggr = self.products_aggr_by_kind.get(product_aggr.product.product_kind_id)
            if cur_aggr:
                cur_aggr.append(product_aggr)
            else:
                cur_aggr = [product_aggr]
                self.products_aggr_by_kind[product_aggr.product.product_kind_id] = cur_aggr

        for key, products in self.products_aggr_by_kind.items():
            self.products_aggr_by_kind[key] = sorted(products, key=operator.attrgetter('product.product_name'))

    def update_sell_categories_aggr(self):
        for value in self.kinds_aggr.values():
            cur_category_aggr = self.categories_aggr.get(value.category.id)
            if cur_category_aggr:
                cur_category_aggr.add_kind_aggr(value)
            else:
                self.categories_aggr[value.category.id] = ProductSellProfitReport.ProductCategoryAggr(value)

            value.set_products(self.products_aggr_by_kind.get(value.kind.id))

        # сортируем виды по имени
        for value in self.categories_aggr.values():
            value.kinds_aggr = sorted(value.kinds_aggr, key=operator.attrgetter('kind.kind_name'))

    def update_sell_groups_aggr(self):
        for value in self.categories_aggr.values():
            cur_group_aggr = self.groups_aggr.get(value.group.group_name)
            if cur_group_aggr:
                cur_group_aggr.add_category_aggr(value)
            else:
                self.groups_aggr[value.group.group_name] = ProductSellProfitReport.ProductGroupAggr(value)

        for item in self.groups_aggr.values():
            item.profit_percent = item.profit_cost / (item.sell_cost / 100)
            self.total_cost_amount += item.sell_cost
            self.total_profit_amount += item.profit_cost
        if self.total_profit_amount > 0:
            self.total_percent = self.total_profit_amount / (self.total_cost_amount / 100)

        # сортируем категории по имени
        for value in self.groups_aggr.values():
            value.categories_aggr = sorted(value.categories_aggr, key=operator.attrgetter('category.category_name'))

    def process(self):
        # берем продажи за период для построения статистики
        sells = self.get_sells()

        for sell in sells:
            shipments = sell.get_shipments(self.filtered_product_kind_ids)
            if len(shipments) > 0:
                cur_products_aggr = self.get_sell_products_aggr(shipments)
                cur_sell_kinds_aggr = self.get_sell_kinds_aggr(shipments)
                self.update_sell_products_aggr(cur_products_aggr)   # обновляем статистику по товарам
                self.update_sell_kinds_aggr(cur_sell_kinds_aggr)    # обновляем статистику по видам
                self.update_rebate_amount(sell)

        if sells:
            self.update_products_aggr()
            self.update_sell_categories_aggr()
            self.update_sell_groups_aggr()

        return self

    def get_sells(self):
        if len(self.sells) > 0:
            return self.sells

        return ProductSell.objects.filter(sell_date__range=(self.start_date, self.end_date))

    def update_rebate_amount(self, sell):
        if sell.rebate > 0:
            self.total_rebate_amount += sell.get_rebate_amount()

    def __str__(self):
        return 'Отчет по прибыли с %s по %s' % (format_date(self.start_date), format_date(self.end_date))


class CustomerSellProfitReport:

    def __init__(self, start_date, end_date, product_kind_ids, customer_ids):
        super(CustomerSellProfitReport, self).__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.product_kind_ids = product_kind_ids
        self.customer_ids = customer_ids
        self.filtered_product_ids = []

        self.customers_aggr = {}

        self.total_cost_amount = 0
        self.total_profit_amount = 0
        self.total_percent = 0
        self.total_rebate_amount = 0

        self.sells = None

    class ProductCustomerAggr(object):

        def __init__(self, customer, profit_report):
            super(CustomerSellProfitReport.ProductCustomerAggr, self).__init__()
            self.customer = customer
            self.profit_report = profit_report

            self.total_cost_amount = profit_report.total_cost_amount
            self.total_profit_amount = profit_report.total_profit_amount
            self.total_percent = profit_report.total_percent
            self.total_rebate_amount = profit_report.total_rebate_amount

    def get_sells(self):
        if self.sells is not None:
            return self.sells

        date_criteria = Q(sell_date__range=(self.start_date, self.end_date))
        customer_criteria = Q()

        if self.customer_ids:
            customer_criteria = Q(customer_id__in=self.customer_ids)
        if self.product_kind_ids:
            self.filtered_product_ids = Product.objects.filter(product_kind__in=self.product_kind_ids).values_list('pk', flat=True)
            product_kind_criteria = Q(shipments__product_id__in=self.filtered_product_ids)

        # TODO почему то в запросе продаж не учитываются ID группы товара
        sell_query = ProductSell.objects \
            .select_related('customer__customer_type') \
            .filter(date_criteria & customer_criteria)

        self.sells = sell_query
        return self.sells

    def process(self):
        sells = self.get_sells()
        customer_sells_map = {}

        for sell in sells:
            customer_id = sell.customer_id
            customer_list = customer_sells_map.get(customer_id)
            if customer_list:
                customer_list.append(sell)
            else:
                customer_sells_map[customer_id] = [sell]

        for customer_id, sells in customer_sells_map.items():
            customer = sells[0].customer
            profit_report = ProductSellProfitReport(self.start_date, self.end_date, sells, self.product_kind_ids).process()
            self.customers_aggr[customer.name] = CustomerSellProfitReport.ProductCustomerAggr(customer, profit_report)

        self.__update_total_amount()

        return self

    def __update_total_amount(self):
        self.total_cost_amount = 0
        self.total_profit_amount = 0
        self.total_percent = 0
        self.total_rebate_amount = 0

        for customer, profit_report in self.customers_aggr.items():
            self.total_cost_amount += profit_report.total_cost_amount
            self.total_profit_amount += profit_report.total_profit_amount
            self.total_rebate_amount += profit_report.total_rebate_amount

        if self.total_profit_amount > 0:
            self.total_percent = self.total_profit_amount / (self.total_cost_amount / 100)

    def __str__(self):
        return 'Отчет по покупателям с %s по %s' % (format_date(self.start_date), format_date(self.end_date))

