from django.contrib import admin

from src.apps.cashbox.models import CashBox, CashTake, ProductSell


@admin.register(CashBox)
class CashBoxAdmin(admin.ModelAdmin):

    list_display = ['cash_type', 'cash']
    actions = None


@admin.register(CashTake)
class CashTakeAdmin(admin.ModelAdmin):

    date_hierarchy = 'take_date'
    list_display = ['get_take_date', 'cash_type', 'cash']
    list_per_page = 50
    actions = None

    def get_take_date(self, obj):
        return obj.get_verbose_take_date()
    get_take_date.short_description = 'Дата изъятия'


@admin.register(ProductSell)
class ProductSellAdmin(admin.ModelAdmin):

    date_hierarchy = 'sell_date'
    list_display = ['get_verbose_sell_date', 'seller', 'get_sell_amount']
    list_per_page = 50
    ordering = ['-sell_date']
    actions = None

    def get_verbose_sell_date(self, obj):
        return obj.get_verbose_sell_date()
    get_verbose_sell_date.short_description = 'Дата продажи'

    def get_sell_amount(self, obj):
        return obj.get_sell_amount()
    get_sell_amount.short_description = 'Сумма продажи'

    def get_queryset(self, request):
        qs = super(ProductSellAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(seller=request.user)
