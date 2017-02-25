
from django.db import models
from django.db import transaction

from hookah_crm import settings
from src.template_tags.common_tags import format_date, round_number

STORAGE_PERMS = {
    'view_product': 'storage.view_product',
    'import_revise': 'storage.import_revise',
}


class ProductGroup(models.Model):

    group_name = models.CharField(u'Название группы товара', max_length=20, unique=True)

    def __str__(self):
        return self.group_name

    class Meta:
        verbose_name = u'Группа товара'
        verbose_name_plural = u'Группы товара'
        db_table = 'storage_product_group'


class ProductCategory(models.Model):

    product_group = models.ForeignKey(to=ProductGroup, verbose_name=u'Группа товара', on_delete=models.PROTECT)
    category_name = models.CharField(u'Название категории товара', max_length=20, db_index=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = u'Категория товара'
        verbose_name_plural = u'Категории товара'
        db_table = 'storage_product_category'


class ProductKind(models.Model):

    product_category = models.ForeignKey(to=ProductCategory, verbose_name=u'Категория товара', on_delete=models.PROTECT)
    kind_name = models.CharField(u'Название вида товара', max_length=40, db_index=True)
    min_count = models.IntegerField(u'Минимальное количество', default=10)
    need_update_products = models.BooleanField(u'Обновлять стоимость товаров при приемке', default=False)

    def __str__(self):
        return self.kind_name

    class Meta:
        verbose_name = u'Вид товара'
        verbose_name_plural = u'Виды товара'
        db_table = 'storage_product_kind'


class ProductProvider(models.Model):

    provider_name = models.CharField(u'Поставщик товара', max_length=30, unique=True)
    description = models.CharField(u'Краткое описание', max_length=300)

    def __str__(self):
        return self.provider_name

    class Meta:
        verbose_name = u'Поставщик товара'
        verbose_name_plural = u'Поставщики товара'
        db_table = 'storage_product_provider'


class Product(models.Model):

    product_kind = models.ForeignKey(to='ProductKind', verbose_name=u'Вид товара', on_delete=models.PROTECT)
    product_name = models.CharField(u'Наименование', max_length=100, db_index=True)
    product_image = models.ImageField(u'Картинка', upload_to='storage/products', blank=True)
    cost_price = models.DecimalField(u'Себестоимость', max_digits=10, decimal_places=2)
    price_retail = models.DecimalField(u'Розница', max_digits=10, decimal_places=2)
    price_discount = models.DecimalField(u'Дисконт', max_digits=10, decimal_places=2)
    price_wholesale = models.DecimalField(u'Оптом', max_digits=10, decimal_places=2)
    price_shop = models.DecimalField(u'Заведение', max_digits=10, decimal_places=2)
    product_count = models.IntegerField(u'Количество')
    min_count = models.IntegerField(u'Минимальное количество')

    def get_storage_count(self):
        return self.product_count

    def __str__(self):
        return '%s' % self.product_name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        db_table = 'storage_product'
        permissions = [
            ('view_product', u'Просмотр товара'),
        ]


class Shipment(models.Model):

    product = models.ForeignKey(to='Product', verbose_name=u'Товар', on_delete=models.PROTECT)
    cost_price = models.DecimalField(u'Себестоимость', max_digits=10, decimal_places=2)
    product_count = models.IntegerField(u'Количество')

    def __str__(self):
        return '%s/%s/%s - стоимость партии товара %s' \
               % (self.product.product_name, self.cost_price, self.product_count, self.cost_price * self.product_count)

    def get_shipment_amount(self):
        return self.cost_price * self.product_count

    class Meta:
        verbose_name = u'Партия товара'
        verbose_name_plural = u'Партии товаров'
        db_table = 'storage_shipment'


class Invoice(models.Model):

    INVOICE_STATUS = (
        ('DRAFT', 'Черновик'),
        ('ACCEPT', 'Принято'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Приемщик', related_name='invoices', on_delete=models.PROTECT)
    invoice_date = models.DateTimeField(u'Дата поступления')
    shipments = models.ManyToManyField(to='Shipment', verbose_name=u'Товары', related_name='invoices')
    product_provider = models.ForeignKey(to='ProductProvider', verbose_name='Поставщик', on_delete=models.PROTECT)
    overhead = models.DecimalField(u'Накладные расходы', max_digits=10, decimal_places=2)
    status = models.CharField(u'Статус', choices=INVOICE_STATUS, max_length=6)

    def __str__(self):
        return u'Приемка товара от %s' % self.get_formatted_date()

    def get_formatted_date(self):
        return format_date(self.invoice_date)

    def get_total_amount(self):
        amount = 0
        for shipment in self.shipments.all():
            amount += shipment.get_shipment_amount()
        return round_number(amount, 2)

    class Meta:
        verbose_name = u'Приемка товара'
        verbose_name_plural = u'Приемка товара'
        db_table = 'storage_invoice'


class ProductRevise(models.Model):

    product = models.ForeignKey(to='Product', verbose_name=u'Товар для сверки', on_delete=models.PROTECT)
    count_revise = models.IntegerField(u'Количество по сверке')
    count_storage = models.IntegerField(u'Количество на складе')
    revise = models.ForeignKey(to='Revise', verbose_name=u'Сверка', on_delete=models.PROTECT, null=True)

    def update_product_count_by_revise(self):
        self.product.product_count = self.count_revise
        self.product.save()

    def revert_product_count_to_storage(self):
        self.product.product_count = self.count_storage
        self.product.save()

    def get_loss_cost_price(self):
        return round((self.count_revise - self.count_storage) * self.product.cost_price, 2)

    def get_loss_retail_price(self):
        return round((self.count_revise - self.count_storage) * self.product.price_retail, 2)

    def get_loss_discount_price(self):
        return round((self.count_revise - self.count_storage) * self.product.price_discount, 2)

    def get_loss_shop_price(self):
        return round((self.count_revise - self.count_storage) * self.product.price_shop, 2)

    def get_loss_wholesale_price(self):
        return round((self.count_revise - self.count_storage) * self.product.price_wholesale, 2)

    def __str__(self):
        return 'Сверка товара - %s' % str(self.product)

    class Meta:
        verbose_name = u'Товар для сверки'
        verbose_name_plural = u'Товары для сверки'
        db_table = 'storage_product_revise'


class Revise(models.Model):

    REVISE_STATUS = (
        ('DRAFT', u'Черновик'),
        ('ACCEPT', u'Принята'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Сверку совершил', related_name='revises', on_delete=models.PROTECT)
    status = models.CharField(u'Статус сверки', choices=REVISE_STATUS, max_length=7, default='DRAFT')
    revise_date = models.DateTimeField(u'Дата сверки')
    products_revise = models.ManyToManyField(to='ProductRevise', verbose_name=u'Товары для сверки', related_name='revises')

    def get_verbose_revise_date(self):
        return format_date(self.revise_date)

    @transaction.atomic
    def accept_revise(self):
        for product_revise in self.products_revise.select_related().all():
            product_revise.update_product_count_by_revise()
        self.status = 'ACCEPT'
        self.save()

    def calculate_loss(self):
        products_revise = self.products_revise.select_related().all()

        loss_cost_price = 0
        loss_retail_price = 0
        loss_discount_price = 0
        loss_shop_price = 0
        loss_wholesale_price = 0

        for product_revise in products_revise:
            loss_cost_price += product_revise.get_loss_cost_price()
            loss_retail_price += product_revise.get_loss_retail_price()
            loss_discount_price += product_revise.get_loss_discount_price()
            loss_shop_price += product_revise.get_loss_shop_price()
            loss_wholesale_price += product_revise.get_loss_wholesale_price()

        self.loss_cost_price = round_number(loss_cost_price, 2)
        self.loss_retail_price = round_number(loss_retail_price, 2)
        self.loss_discount_price = round_number(loss_discount_price, 2)
        self.loss_shop_price = round_number(loss_shop_price, 2)
        self.loss_wholesale_price = round_number(loss_wholesale_price, 2)

        self.cache_products_revise = products_revise

    def __str__(self):
        return 'Сверка товаров от %s' % format_date(self.revise_date)

    class Meta:
        verbose_name = u'Сверка товара'
        verbose_name_plural = u'Сверки товаров'
        db_table = 'storage_revise'
