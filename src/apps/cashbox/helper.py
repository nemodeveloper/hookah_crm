import operator
from datetime import datetime

from dateutil.relativedelta import relativedelta
from openpyxl import Workbook

from hookah_crm import settings
from src.apps.cashbox.models import ProductSell
from src.apps.ext_user.models import ExtUser, WorkProfile
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

    def __init__(self, start_date, end_date):
        super(ProductSellReportForPeriod, self).__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.user = request.get_current_user()
        self.sells = []
        self.total_amount = 0
        self.total_rebate_amount = 0
        self.payments = {}

    def process(self):

        sells = ProductSell.objects.prefetch_related('shipments', 'payments')
        if not self.user.is_superuser:
            sells = sells.filter(seller_id=self.user.id)

        self.sells = sells.filter(sell_date__range=(self.start_date, self.end_date)).order_by('-sell_date')

        # TODO решить проблему с многочисленными запросами партий товара
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

    def __init__(self, start_date, end_date):
        super(ProductSellProfitReport, self).__init__()
        self.start_date = start_date
        self.end_date = end_date

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
            self.total_percent += item.profit_percent
        if self.total_percent > 0:
            self.total_percent /= len(self.groups_aggr.values())

        # сортируем категории по имени
        for value in self.groups_aggr.values():
            value.categories_aggr = sorted(value.categories_aggr, key=operator.attrgetter('category.category_name'))

    def process(self):
        # берем продажи за период для построения статистики
        sells = ProductSell.objects.prefetch_related('shipments').\
            filter(sell_date__range=(self.start_date, self.end_date))

        for sell in sells:
            shipments = sell.get_shipments()
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

    def update_rebate_amount(self, sell):

        if sell.rebate > 0:
            self.total_rebate_amount += sell.get_rebate_amount()

    def __str__(self):
        return 'Отчет по прибыли с %s по %s' % (format_date(self.start_date), format_date(self.end_date))


class ProductSellCheckOperation(object):

    def __init__(self, sell_id):
        super(ProductSellCheckOperation, self).__init__()
        self.sell = ProductSell.objects.prefetch_related('shipments', 'payments').get(id=sell_id)
        self.check_name = 'SellCheck_%s' % format_date(self.sell.sell_date, '%Y_%m_%d_%H_%M')

    @staticmethod
    def post_process_sheet(sheet):
        dims = {}
        for row in sheet.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))
        for col, value in dims.items():
            sheet.column_dimensions[col].width = value + 5

    def get_excel_check(self):

        book = Workbook()
        sheet = book.create_sheet(title='Чек по продаже', index=0)

        sheet.append(['Продажа от %s' % self.sell.get_verbose_sell_date()])
        sheet.append(['Список товаров продажи:'])
        sheet.append(['№', 'Группа', 'Категория', 'Вид', 'Наименование', 'Количество', 'Цена(шт)', 'Сумма'])

        cur = 1
        for shipment in self.sell.get_shipments():
            product = shipment.product
            product_category = product.product_kind.product_category
            sheet.append([cur, product_category.product_group.group_name,
                          product_category.category_name,
                          product.product_kind.kind_name,
                          product.product_name, shipment.product_count, shipment.cost_price, shipment.get_shipment_amount()])
            cur += 1
        sheet.append(['', '', '', '', '', '', 'Итого', self.sell.get_sell_amount()])
        sheet.append([])

        cur = 1
        sheet.append(['Оплата:'])
        sheet.append(['№', 'Тип', 'Сумма'])
        for payment in self.sell.get_payments():
            sheet.append([cur, payment.get_cash_type_display(), payment.cash])
            cur += 1
        sheet.append(['', 'Итого', self.sell.get_payment_amount()])

        self.post_process_sheet(sheet)

        return book

