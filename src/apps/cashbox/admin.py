from django.contrib import admin

from src.apps.cashbox.models import ProductSell


@admin.register(ProductSell)
class ProductSellAdmin(admin.ModelAdmin):

    date_hierarchy = 'sell_date'
    list_display = ['id', 'get_verbose_sell_date', 'seller', 'customer', 'get_customer_type', 'get_sell_amount', 'rebate']
    list_filter = ['customer__customer_type__type_name', 'customer__name']
    list_per_page = 20
    ordering = ['-sell_date']
    actions = None
    show_full_result_count = False

    def get_verbose_sell_date(self, obj):
        return obj.get_verbose_sell_date()
    get_verbose_sell_date.short_description = 'Дата продажи'

    def get_customer_type(self, obj):
        return obj.customer.customer_type.type_name
    get_customer_type.short_description = 'Тип покупателя'

    def get_sell_amount(self, obj):
        return obj.get_sell_amount()
    get_sell_amount.short_description = 'Сумма продажи'

    def get_queryset(self, request):
        qs = super(ProductSellAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(seller=request.user)
