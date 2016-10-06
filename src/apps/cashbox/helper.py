from datetime import datetime

from dateutil.relativedelta import relativedelta

from hookah_crm import settings
from src.apps.cashbox.models import ProductSell, CashBox
from src.apps.ext_user.models import ExtUser, WorkProfile, WorkSession
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

        self.__process()

    def __process(self):
        if self.user.is_superuser:
            sells = ProductSell.objects.prefetch_related().filter(
                sell_date__range=(self.start_date, self.end_date)).order_by('sell_date')
        else:
            sells = ProductSell.objects.prefetch_related().filter(
                sell_date__range=(self.start_date, self.end_date)).filter(seller=self.user).order_by('sell_date')

        if sells:
            self.sells = sells
            for sell in sells:
                self.total_amount += float(sell.get_sell_amount())
                self.__process_payments(sell.payments.all())

    def __process_payments(self, payments):
        for payment in payments:
            if not self.payments.get(payment.get_cash_type_display()):
                self.payments[payment.get_cash_type_display()] = 0
            self.payments[payment.get_cash_type_display()] += float(payment.cash)

    def __str__(self):
        return 'Список продаж товара с %s по %s' % (format_date(self.start_date), format_date(self.end_date))


class ProductSellCreditReport(object):

    def __init__(self, start_date, end_date):
        super(ProductSellCreditReport, self).__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.sells = []
        self.credit_amount = 0
        self.credit_cashbox_amount = CashBox.objects.get(cash_type='CREDIT').cash
        self.amount_dif = self.credit_cashbox_amount
        self.__process()

    def __process(self):
        self.sells = ProductSell.objects.prefetch_related().filter(payments__cash_type='CREDIT').filter(sell_date__range=(self.start_date, self.end_date))
        if self.sells:
            for sell in self.sells:
                self.credit_amount += sell.get_credit_payment_amount()
            self.amount_dif -= self.credit_amount

    def __str__(self):
        return 'Список должников с %s по %s' % (format_date(self.start_date), format_date(self.end_date))


class ProductSellProfitReport(object):

    def __init__(self, start_date, end_date):
        super(ProductSellProfitReport, self).__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.sell_count = 0

        self.sell_amount = 0
        self.average_check = 0

        self.profit_amount = 0
        self.profit_percent = 0

        self.__process()

    def __process(self):
        sells = ProductSell.objects.prefetch_related().filter(sell_date__range=(self.start_date, self.end_date))
        if sells:
            self.sell_count = sells.count()
            for sell in sells:
                self.sell_amount += float(sell.get_sell_amount())
                self.profit_amount += sell.get_profit_amount()
            self.average_check = self.sell_amount / self.sell_count                         # средний чек
            self.profit_percent = (self.profit_amount / self.sell_amount) * 100     # процент прибыли

    def __str__(self):
        return 'Отчет по прибыли с %s по %s' % (format_date(self.start_date), format_date(self.end_date))
