
from django.db import models

from hookah_crm import settings


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
    cost_price = models.DecimalField(u'Себестоимость', max_digits=8, decimal_places=2)
    price_retail = models.DecimalField(u'Розница', max_digits=8, decimal_places=2)
    price_discount = models.DecimalField(u'Дисконт', max_digits=8, decimal_places=2)
    price_wholesale = models.DecimalField(u'Оптом', max_digits=8, decimal_places=2)
    price_shop = models.DecimalField(u'Заведение', max_digits=8, decimal_places=2)

    def get_storage_count(self):
        storage = ProductStorage.objects.filter(product=self).first()
        if storage:
            return storage.product_count
        return 0

    def __str__(self):
        return '%s' % self.product_name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        db_table = 'storage_product'


class Shipment(models.Model):

    product = models.ForeignKey(to='Product', verbose_name=u'Товар')
    cost_price = models.DecimalField(u'Себестоимость', max_digits=8, decimal_places=2)
    product_count = models.IntegerField(u'Количество')

    def __str__(self):
        return '%s/%s/%s - стоимость партии товара %s' \
               % (self.product.product_name, self.cost_price, self.product_count, self.cost_price * self.product_count)

    def get_product_amount(self):
        return self.cost_price * self.product_count

    class Meta:
        verbose_name = u'Партия товара'
        verbose_name_plural = u'Партии товаров'
        db_table = 'storage_shipment'


class Invoice(models.Model):

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'Приемщик', related_name='invoices')
    invoice_date = models.DateTimeField(u'Дата поступления')
    shipments = models.ManyToManyField(to='Shipment', verbose_name=u'Товары', related_name='invoices')
    product_provider = models.ForeignKey(to='ProductProvider', verbose_name='Поставщик', on_delete=models.PROTECT)
    overhead = models.DecimalField(u'Накладные расходы', max_digits=7, decimal_places=2)

    def __str__(self):
        return u'Приемка товара от %s' % self.get_formatted_date()

    def get_formatted_date(self):
        return self.invoice_date.strftime(settings.DATE_FORMAT)

    def get_total_amount(self):
        amount = 0
        for shipment in self.shipments.all():
            amount += shipment.get_product_amount()
        return amount

    class Meta:
        verbose_name = u'Приемка товара'
        verbose_name_plural = u'Приемка товара'
        db_table = 'storage_invoice'


class ProductStorage(models.Model):

    product = models.OneToOneField(to='Product', verbose_name=u'Товар',
                                   related_name='product_storage', on_delete=models.PROTECT)
    product_count = models.IntegerField(u'Количество')
    min_count = models.IntegerField(u'Минимальное количество')

    def __str__(self):
        return '%s/%s' % (self.product.product_name, self.product_count)

    class Meta:
        verbose_name = u'Товар на складе'
        verbose_name_plural = u'Товары на складе'
        db_table = 'storage_product_storage'
