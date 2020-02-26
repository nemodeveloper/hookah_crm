
from django.db import models
from django.db import transaction

from hookah_crm import settings
from src.apps.market.models import Customer
from src.apps.storage.models import Product
from src.common_helper import date_to_verbose_format
from src.template_tags.common_tags import format_date, round_number

MoneyType = (
    ('CASH', u'Наличные'),
    ('CARD', u'Пластиковая карта'),
    ('CREDIT', u'Долг'),
)


class PaymentType(models.Model):
    sell = models.ForeignKey(to='cashbox.ProductSell', verbose_name=u'Продажа', related_name='payments', null=True, on_delete=models.CASCADE)
    cash_type = models.CharField(u'Тип оплаты', choices=MoneyType, max_length=18)   # TODO можно бы перейти на справочник
    cash = models.DecimalField(u'Сумма', max_digits=10, decimal_places=2)
    description = models.CharField(u'Доп.информация', max_length=300, null=True, blank=True)

    def __str__(self):
        return 'Сумма %s оплата %s' % (self.cash, self.get_cash_type_display())

    class Meta:
        verbose_name = u'Платеж'
        verbose_name_plural = u'Платежи'
        db_table = 'cashbox_payment_type'


class ProductShipment(models.Model):

    sell = models.ForeignKey(to='cashbox.ProductSell', verbose_name=u'Продажа', related_name='shipments', null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(to='storage.Product', verbose_name=u'Товар', on_delete=models.PROTECT)
    cost_price = models.DecimalField(u'Фактическая стоимость', max_digits=10, decimal_places=2)
    initial_cost_price = models.DecimalField(u'Первоначальная стоимость', max_digits=10, decimal_places=2)
    product_cost_price = models.DecimalField(u'Себестоимость товара при продаже', max_digits=10, decimal_places=2)
    product_count = models.IntegerField(u'Количество')

    def roll_back_product_to_storage(self):
        product = Product.objects.select_for_update(nowait=True).get(id=self.product_id)
        product.product_count += self.product_count
        product.save()

    def take_product_from_storage(self):
        product = Product.objects.select_for_update(nowait=True).get(id=self.product_id)
        product.product_count -= self.product_count
        product.save()

    # получить сумму фактической продажи со скидкой если таковая была в продаже
    def get_shipment_amount(self):
        return self.cost_price * self.product_count

    # получить первоначальную сумму продажи используется для отчетности
    def get_initial_amount(self):
        return self.initial_cost_price * self.product_count

    # получить сумму продажи по себестоимости
    def get_cost_amount(self):
        return self.product_cost_price * self.product_count

    def __str__(self):
        return '%s/%s/%s - стоимость товара %s' \
               % (self.product.product_name, self.cost_price, self.product_count, self.cost_price * self.product_count)

    class Meta:
        verbose_name = u'Проданный товар'
        verbose_name_plural = u'Проданный товар'
        db_table = 'cashbox_shipment'


class ProductSell(models.Model):

    SELL_STATE_CHOICES = (
        ('DRAFT', u'Черновик'),
        ('EXECUTED', u'Оформлена'),
        ('CANCELED', u'Отменена'),
    )

    sell_date = models.DateTimeField(u'Время продажи', db_index=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Продавец', related_name='sell_products', on_delete=models.PROTECT)
    rebate = models.DecimalField(u'Скидка(%)', max_digits=4, decimal_places=2, default=0)
    customer = models.ForeignKey(to=Customer, verbose_name=u'Покупатель', on_delete=models.PROTECT, db_index=True)

    # Провести продажу
    # 1)списать товары со склада
    @transaction.atomic
    def make_sell(self):
        # Списываем товары с учетом скидки
        for shipment in self.get_shipments():
            shipment.take_product_from_storage()
            if self.rebate > 0:
                # Обновим фактическую стоимость продажи
                shipment.cost_price -= shipment.cost_price / 100 * self.rebate
                shipment.save()
        self.save()

    def get_shipments(self, filtered_product_kind_ids=()):
        if hasattr(self, '_shipments'):
            return self._shipments

        # почему то идут лишние выборки? смотри отчет по спектру лофт ленина с 3 по 23 всего 10 пачек но выбрано 100!
        self._shipments = self.shipments.select_related().all().order_by('id') if len(filtered_product_kind_ids) == 0 \
            else self.shipments.select_related().filter(product__product_kind__in=filtered_product_kind_ids).order_by('id')
        return self._shipments

    def get_payments(self):
        if hasattr(self, '_payments'):
            return self._payments

        self._payments = self.payments.all()
        return self._payments

    # Получить фактическую сумму продажи
    def get_sell_amount(self):
        if hasattr(self, '_sell_amount'):
            return self._sell_amount
        else:
            amount = 0
            for shipment in self.get_shipments():
                amount += shipment.get_shipment_amount()
            self._sell_amount = round_number(amount, 2)
        return self._sell_amount

    # Получить первоначальную сумму продажи без скидки
    def get_initial_sell_amount(self):

        if self.rebate == 0:
            return self.get_sell_amount()

        if hasattr(self, '_initial_sell_amount'):
            return self._initial_sell_amount
        else:
            amount = 0
            for shipment in self.get_shipments():
                amount += shipment.get_initial_amount()
            self._initial_sell_amount = round_number(amount, 2)
        return self._initial_sell_amount

    # Получить сумму скидку
    def get_rebate_amount(self):
        if self.rebate > 0:
            return self.get_initial_sell_amount() - self.get_sell_amount()
        return 0

    def get_payment_amount(self):
        amount = 0
        for payment in self.get_payments():
            amount += payment.cash
        return round_number(amount, 2)

    def get_credit_payment_amount(self):
        amount = 0
        for payment in self.get_payments():
            if payment.cash_type == 'CREDIT':
                amount += payment.cash
        return round_number(amount, 2)

    def get_cost_amount(self):
        amount = 0
        for shipment in self.get_shipments():
            amount += shipment.get_cost_amount()
        return round_number(amount, 2)

    # Получить чистую прибыль
    def get_profit_amount(self):
        raw_amount = self.get_sell_amount()
        cost_amount = float(self.get_cost_amount())
        return round_number(raw_amount - cost_amount, 2)

    def get_credit_info(self):
        for payment in self.get_payments():
            if payment.cash_type == 'CREDIT':
                return payment.description

    def get_verbose_sell_date(self):
        return format_date(self.sell_date)

    def __str__(self):
        return '%s - %s' % (date_to_verbose_format(self.sell_date), str(self.seller))

    def get_log_info(self):
        shipment_info = ''
        for shipment in self.get_shipments():
            shipment_info += 'id партии товара - %s\nтовар - %s\nтовара на складе - %s\nтовара к продаже - %s\nсумма - %s\n' \
                             % (shipment.id, shipment.product, shipment.product.product_count, shipment.product_count, shipment.get_shipment_amount())
        return 'Продавец %s добавил продажу id - %s, время %s, товары:\n%s' % (self.seller, self.id, format_date(self.sell_date), shipment_info)

    class Meta:
        verbose_name = u'Продажа'
        verbose_name_plural = u'Продажи'
        db_table = 'cashbox_product_sell'
