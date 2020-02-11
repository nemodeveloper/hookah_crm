from django.contrib import admin

from src.apps.cashbox.models import ProductSell


RETAIL_CUSTOMER = u'Розница'


@admin.register(ProductSell)
class ProductSellAdmin(admin.ModelAdmin):

    date_hierarchy = 'sell_date'
    list_display = ['id', 'get_verbose_sell_date', 'seller', 'get_customer', 'get_sell_amount', 'rebate']
    list_filter = ['customer__customer_type__type_name', 'customer__name']
    list_per_page = 20
    ordering = ['-sell_date']
    actions = None
    show_full_result_count = False

    def get_verbose_sell_date(self, obj):
        return obj.get_verbose_sell_date()
    get_verbose_sell_date.short_description = 'Дата продажи'

    def get_customer(self, obj):
        return obj.customer.name if obj.customer.name == RETAIL_CUSTOMER \
            else obj.customer.customer_type.type_name + ' / ' + obj.customer.name
    get_customer.short_description = 'Покупатель'

    def get_sell_amount(self, obj):
        return obj.get_sell_amount()
    get_sell_amount.short_description = 'Сумма продажи'

    def get_queryset(self, request):
        qs = super(ProductSellAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(seller=request.user)
