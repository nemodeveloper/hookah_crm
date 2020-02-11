from django.contrib import admin

from src.apps.market.forms import CustomerAdminForm
from src.apps.market.models import CustomerType, Customer


@admin.register(CustomerType)
class CustomerTypeAdmin(admin.ModelAdmin):
    list_display = ['type_name']
    list_per_page = 30
    ordering = ['type_name']
    actions = None
    show_full_result_count = False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm
    list_display = ['name', 'get_verbose_customer_type']
    list_per_page = 30
    actions = None
    show_full_result_count = False
    list_filter = ['customer_type__type_name']
    search_fields = ('name',)
    ordering = ['name']

    def get_verbose_customer_type(self, obj):
        return obj.get_verbose_customer_type()
    get_verbose_customer_type.short_description = u'Тип покупателя'
