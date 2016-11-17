import operator
from datetime import datetime

from dateutil.relativedelta import relativedelta

from hookah_crm import settings
from src.apps.cashbox.models import ProductSell, CashBox
from src.apps.ext_user.models import ExtUser, WorkProfile, WorkSession
from src.apps.storage.models import ProductCategory
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
            return float(self.product_sell.get_sell_amount()) / 100 * self.percent

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
        profile = WorkProfile.objects.get(ext_user=self.user)
        if not profile:
            self.is_admin = True
            return

        product_sells = ProductSell.objects.prefetch_related('shipments', 'payments')\
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

    def __init__(self, user_id, start_date, end_date):
        super(ProductSellReportForPeriod, self).__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.user = ExtUser.objects.get(id=user_id)
        self.sells = []
        self.total_amount = 0
        self.payments = {}

    def process(self):
        if self.user.is_superuser:
            self.sells = ProductSell.objects.prefetch_related('shipments', 'payments').\
                filter(sell_date__range=(self.start_date, self.end_date)).\
                order_by('-sell_date')
        else:
            self.sells = ProductSell.objects.prefetch_related('shipments', 'payments').\
                filter(seller=self.user).\
                filter(sell_date__range=(self.start_date, self.end_date)).\
                order_by('-sell_date')

        if self.sells:
            for sell in self.sells:
                self.total_amount += float(sell.get_sell_amount())
                self.__process_payments(sell.payments.all())

        return self

    def __process_payments(self, payments):
        for payment in payments:
            if not self.payments.get(payment.get_cash_type_display()):
                self.payments[payment.get_cash_type_display()] = 0
            self.payments[payment.get_cash_type_display()] += round(float(payment.cash), 2)

    def __str__(self):
        return 'Список продаж товара с %s по %s' % (format_date(self.start_date), format_date(self.end_date))


class ProductSellCreditReport(object):

    def __init__(self, start_date, end_date):
        super(ProductSellCreditReport, self).__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.sells = []
        self.credit_amount = 0
        self.amount_dif = CashBox.objects.get(cash_type='CREDIT').cash

    def process(self):
        self.sells = ProductSell.objects.prefetch_related('payments').select_related().\
            filter(payments__cash_type='CREDIT').\
            filter(sell_date__range=(self.start_date, self.end_date)).\
            order_by('-sell_date')
        if self.sells:
            for sell in self.sells:
                self.credit_amount += sell.get_credit_payment_amount()
            self.amount_dif -= self.credit_amount

        return self

    def __str__(self):
        return 'Список должников с %s по %s' % (format_date(self.start_date), format_date(self.end_date))


class ProductSellProfitReport(object):

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

    class ProductCategoryAggr(object):

        def __init__(self, kind_aggr):
            super(ProductSellProfitReport.ProductCategoryAggr, self).__init__()
            self.sell_cost = 0                  # общая сумма с продаж по категориям
            self.group = kind_aggr.group        # группа товара с которой связана категория товара
            self.category = kind_aggr.category
            self.kinds_aggr = []
            self.add_kind_aggr(kind_aggr)

        def add_kind_aggr(self, kind_aggr):
            self.sell_cost += kind_aggr.sell_cost
            self.kinds_aggr.append(kind_aggr)

    class ProductGroupAggr(object):

        def __init__(self, category_aggr):
            super(ProductSellProfitReport.ProductGroupAggr, self).__init__()
            self.sell_cost = 0              # общая сумма с продаж по группам
            self.group_name = category_aggr.group.group_name
            self.categories_aggr = []
            self.add_category_aggr(category_aggr)

        def add_category_aggr(self, category_aggr):
            self.sell_cost += category_aggr.sell_cost
            self.categories_aggr.append(category_aggr)

    def __init__(self, start_date, end_date):
        super(ProductSellProfitReport, self).__init__()
        self.start_date = start_date
        self.end_date = end_date

        self.groups_aggr = {}
        self.categories_aggr = {}
        self.kinds_aggr = {}

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

    def update_sell_kinds_aggr(self, kinds_aggr):
        for key, value in kinds_aggr.items():
            sell_kinds_aggr = self.kinds_aggr.get(key)
            if not sell_kinds_aggr:
                self.kinds_aggr[key] = value
            else:
                sell_kinds_aggr.update(value)

    def update_sell_categories_aggr(self):
        for key, value in self.kinds_aggr.items():
            cur_category_aggr = self.categories_aggr.get(value.category.id)
            if cur_category_aggr:
                cur_category_aggr.add_kind_aggr(value)
            else:
                self.categories_aggr[value.category.id] = ProductSellProfitReport.ProductCategoryAggr(value)
        # сортируем виды по имени
        for value in self.categories_aggr.values():
            value.kinds_aggr = sorted(value.kinds_aggr, key=operator.attrgetter('kind.kind_name'))

    def update_sell_groups_aggr(self):
        for key, value in self.categories_aggr.items():
            cur_group_aggr = self.groups_aggr.get(value.group.group_name)
            if cur_group_aggr:
                cur_group_aggr.add_category_aggr(value)
            else:
                self.groups_aggr[value.group.group_name] = ProductSellProfitReport.ProductGroupAggr(value)
        # сортируем категории по имени
        for value in self.groups_aggr.values():
            value.categories_aggr = sorted(value.categories_aggr, key=operator.attrgetter('category.category_name'))

    def process(self):
        # берем продажи за период для построения статистики
        sells = ProductSell.objects.prefetch_related('shipments').\
            filter(sell_date__range=(self.start_date, self.end_date))

        if sells:
            for sell in sells:
                cur_sell_kinds_aggr = self.get_sell_kinds_aggr(sell.shipments.select_related().all())
                self.update_sell_kinds_aggr(cur_sell_kinds_aggr)  # обновляем статистику по видам
            self.update_sell_categories_aggr()
            self.update_sell_groups_aggr()

        return self

    def __str__(self):
        return 'Отчет по прибыли с %s по %s' % (format_date(self.start_date), format_date(self.end_date))
