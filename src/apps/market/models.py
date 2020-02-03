from django.db import models


class CustomerType(models.Model):
    type_name = models.CharField(u'Тип покупателя', max_length=128, null=False, blank=False)

    def __str__(self):
        return '%s' % self.type_name

    class Meta:
        verbose_name = u'Тип покупателей'
        verbose_name_plural = u'Тип покупателя'
        db_table = 'market_customer_types'


class Customer(models.Model):
    name = models.CharField(u'Наименование покупателя', max_length=128, null=False, db_index=True)
    customer_type = models.ForeignKey(to=CustomerType, verbose_name=u'Тип покупателя', on_delete=models.PROTECT)
    main_contact = models.CharField(u'Ответственное лицо', max_length=128, null=True, blank=True)
    phone_number = models.CharField(u'Номер телефона', max_length=128, null=True, blank=True)
    communication_links = models.CharField(u'Ссылки для связи', max_length=512, null=True, blank=True)
    address = models.CharField(u'Адрес', max_length=256, null=True, blank=True)
    description = models.CharField(u'Доп.информация', max_length=512, null=True, blank=True)

    def get_verbose_customer_type(self):
        return self.customer_type.type_name

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = u'Покупатели'
        verbose_name_plural = u'Покупатель'
        db_table = 'market_customers'
