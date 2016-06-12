from django.db import models


class ProductCategory(models.Model):

    category_name = models.CharField(u'Категория товара', max_length=15, unique=True, db_index=True)

    def __str__(self):
        return self.category_name

    class Meta:
        ordering = ['category_name']
        verbose_name = u'Категория товара'
        verbose_name_plural = u'Категории товаров'
        db_table = 'storage_product_category'


class ProductKind(models.Model):

    kind_name = models.CharField(u'Вид товара', max_length=30)

    def __str__(self):
        return self.kind_name

    class Meta:
        ordering = ['kind_name']
        verbose_name = u'Вид товара'
        verbose_name_plural = u'Виды товаров'
        db_table = 'storage_product_kind'


class ProductProvider(models.Model):

    provider_name = models.CharField(u'Поставщик товара', max_length=30)
    description = models.CharField(u'Краткое описание', max_length=200)

    def __str__(self):
        return self.provider_name

    class Meta:
        ordering = ['provider_name']
        verbose_name = u'Поставщик товара'
        verbose_name_plural = u'Поставщики товара'
        db_table = 'storage_product_provider'


class Product(models.Model):

    product_category = models.ForeignKey(to='ProductCategory',
                                         verbose_name=u'Категория товара', on_delete=models.PROTECT)
    product_kind = models.ForeignKey(to='ProductKind',
                                     verbose_name=u'Вид товара', on_delete=models.PROTECT)
    product_name = models.CharField(u'Наименование', max_length=100, unique=True, db_index=True)
    product_image = models.ImageField(u'Картинка', upload_to='storage/products', blank=True)
    cost_price = models.DecimalField(u'Себестоимость', max_digits=8, decimal_places=2)
    price_retail = models.DecimalField(u'Розница', max_digits=8, decimal_places=2)
    price_discount = models.DecimalField(u'Дисконт', max_digits=8, decimal_places=2)
    price_wholesale = models.DecimalField(u'Оптом', max_digits=8, decimal_places=2)

    def __str__(self):
        return '%s/%s' % (self.product_category.category_name, self.product_name)

    class Meta:
        ordering = ['product_name']
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

    class Meta:
        verbose_name = u'Партия товара'
        verbose_name_plural = u'Партии товаров'
        db_table = 'storage_shipment'


class Invoice(models.Model):

    invoice_date = models.DateTimeField(u'Время поступления')
    shipments = models.ManyToManyField(to='Shipment', verbose_name=u'Товары', related_name='invoices')
    product_provider = models.ForeignKey(to='ProductProvider', verbose_name='Поставщик', on_delete=models.PROTECT)
    overhead = models.DecimalField(u'Накладные расходы', max_digits=7, decimal_places=2)

    def __str__(self):
        return u'Накладная от %s' % self.invoice_date.strftime('%Y-%m-%d %H:%M')

    class Meta:
        ordering = ['invoice_date']
        verbose_name = u'Накладная'
        verbose_name_plural = u'Накладые'
        db_table = 'storage_invoice'


class ProductStorage(models.Model):

    product = models.ForeignKey(to='Product', verbose_name=u'Товар',
                                related_name='product_storage', on_delete=models.PROTECT)
    product_count = models.IntegerField(u'Количество')
    min_count = models.IntegerField(u'Минимальное количество')

    def __str__(self):
        return '%s/%s' % (self.product.product_name, self.product_count)

    class Meta:
        verbose_name = u'Склад'
        verbose_name_plural = u'Склад'
        db_table = 'storage_product_storage'
