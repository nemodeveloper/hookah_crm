from django.contrib import admin
from django.db import transaction

from src.apps.cashbox.forms import CashTakeAdminForm
from src.apps.cashbox.models import CashBox, CashTake, ProductSell
from src.apps.cashbox.service import update_cashbox_by_cash_take


@admin.register(CashBox)
class CashBoxAdmin(admin.ModelAdmin):

    list_display = ['cash_type', 'cash']


@admin.register(CashTake)
class CashTakeAdmin(admin.ModelAdmin):

    form = CashTakeAdminForm
    date_hierarchy = 'take_date'
    list_display = ['take_date', 'cash_type', 'cash']
    list_per_page = 20

    @transaction.atomic
    def save_model(self, request, obj, form, change):

        super(CashTakeAdmin, self).save_model(request, obj, form, change)
        update_cashbox_by_cash_take(obj)


@admin.register(ProductSell)
class ProductSellAdmin(admin.ModelAdmin):

    date_hierarchy = 'sell_date'
    list_display = ['sell_date', 'seller']
    filter_horizontal = ['shipments', 'payments']
    list_per_page = 20

    def get_queryset(self, request):

        qs = super(ProductSellAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.filter(seller=request.user)
