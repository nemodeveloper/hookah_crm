from django.db import models

from hookah_crm import settings


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

    def __str__(self):
        return '%s из кассы %s снято %s' % (self.take_date.strftime('%Y-%m-%d %H:%M'),
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


class ProductSell(models.Model):

    sell_date = models.DateTimeField(u'Время продажи', auto_now=True, db_index=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Продавец', related_name='sell_products')
    shipments = models.ManyToManyField(to='storage.Shipment', verbose_name=u'Товары')
    payments = models.ManyToManyField(to='PaymentType', verbose_name=u'Оплата')

    def __str__(self):
        return '%s - %s' % (self.sell_date.strftime('%Y-%m-%d %H:%M'), str(self.seller))

    class Meta:
        verbose_name = u'Продажа'
        verbose_name_plural = u'Продажи'
        db_table = 'cashbox_product_sell'
