
from django.db import models

from hookah_crm import settings
from src.common_helper import date_to_verbose_format
from src.template_tags.common_tags import format_date

MoneyType = (
    ('CASH', u'Наличные'),
    ('CARD', u'Пластиковая карта'),
    ('CREDIT', u'Долг'),
    ('REVISE', u'Сверка')
)


class CashBox(models.Model):

    cash_type = models.CharField(u'Тип кассы', choices=MoneyType, max_length=18, unique=True)
    cash = models.DecimalField(u'Сумма', max_digits=8, decimal_places=2)

    def __str__(self):
        return 'Тип : %s , в кассе %s рублей' % (self.get_cash_type_display(), self.cash)

    class Meta:
        verbose_name = u'Касса'
        verbose_name_plural = u'Кассы'
        db_table = 'cashbox_cashbox'


class CashTake(models.Model):

    take_date = models.DateTimeField(u'Время вывода денег', db_index=True)
    cash_type = models.CharField(u'Тип кассы', choices=MoneyType, max_length=18)
    cash = models.DecimalField(u'Сумма', max_digits=8, decimal_places=2)
    description = models.CharField(u'Доп.информация', max_length=300)

    def get_verbose_take_date(self):
        return self.take_date.strftime(settings.DATE_FORMAT)

    def __str__(self):
        return '%s из кассы %s снято %s' % (self.take_date.strftime(settings.DATE_FORMAT),
                                            self.get_cash_type_display(), self.cash)

    class Meta:

        verbose_name = u'Изьятие денег'
        verbose_name_plural = u'Изьятие денег'
        db_table = 'cashbox_cash_take'


class PaymentType(models.Model):

    cash_type = models.CharField(u'Тип оплаты', choices=MoneyType, max_length=18)
    cash = models.DecimalField(u'Сумма', max_digits=8, decimal_places=2)
    description = models.CharField(u'Доп.информация', max_length=300, null=True, blank=True)

    def __str__(self):
        return 'Сумма %s оплата %s' % (self.cash, self.get_cash_type_display())

    class Meta:
        verbose_name = u'Платеж'
        verbose_name_plural = u'Платежи'
        db_table = 'cashbox_payment_type'


class ProductShipment(models.Model):

    product = models.ForeignKey(to='storage.Product', verbose_name=u'Товар')
    cost_price = models.DecimalField(u'Стоимость', max_digits=8, decimal_places=2)
    product_count = models.IntegerField(u'Количество')

    def get_product_amount(self):
        return self.cost_price * self.product_count

    def get_cost_amount(self):
        return self.product.cost_price * self.product_count

    def __str__(self):
        return '%s/%s/%s - стоимость товара %s' \
               % (self.product.product_name, self.cost_price, self.product_count, self.cost_price * self.product_count)

    class Meta:
        verbose_name = u'Проданный товар'
        verbose_name_plural = u'Проданный товар'
        db_table = 'cashbox_shipment'


class ProductSell(models.Model):

    sell_date = models.DateTimeField(u'Время продажи', db_index=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Продавец', related_name='sell_products')
    shipments = models.ManyToManyField(to='ProductShipment', verbose_name=u'Товары')
    payments = models.ManyToManyField(to='PaymentType', verbose_name=u'Оплата')
    rebate = models.DecimalField(u'Скидка', max_digits=8, decimal_places=2, default=0)

    def get_sell_amount(self):
        amount = 0
        for shipment in self.shipments.all():
            amount += shipment.get_product_amount()
        return '%s' % amount

    def get_payment_amount(self):
        amount = 0
        for payment in self.payments.all():
            amount += payment.cash
        return '%s' % amount

    def get_credit_payment_amount(self):
        amount = 0
        payments = self.payments.filter(cash_type='CREDIT')
        if payments:
            for payment in payments:
                amount += payment.cash
        return amount

    def get_cost_amount(self):
        amount = 0
        for shipment in self.shipments.all():
            amount += shipment.get_cost_amount()
        return amount

    # Получить чистую прибыль
    def get_profit_amount(self):
        raw_amount = float(self.get_sell_amount())
        cost_amount = float(self.get_cost_amount())
        return raw_amount - cost_amount

    def get_credit_info(self):
        payments = self.payments.filter(cash_type='CREDIT')
        info = 'Отсутствует информация по должнику!'
        if payments:
            info = payments[0].description
        return info

    def get_verbose_sell_date(self):
        return date_to_verbose_format(self.sell_date)

    def __str__(self):
        return '%s - %s' % (date_to_verbose_format(self.sell_date), str(self.seller))

    def get_log_info(self):
        return 'Продавец %s добавил продажу, время %s, сумма %s' % (self.seller, format_date(self.sell_date), self.get_payment_amount())

    class Meta:
        verbose_name = u'Продажа'
        verbose_name_plural = u'Продажи'
        db_table = 'cashbox_product_sell'
