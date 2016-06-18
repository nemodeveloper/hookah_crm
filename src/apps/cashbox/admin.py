from django.contrib import admin


from src.apps.cashbox.forms import CashTakeForm, PaymentTypeForm
from src.apps.cashbox.models import CashBox, CashTake, PaymentType, ProductSell


@admin.register(CashBox)
class CashBoxAdmin(admin.ModelAdmin):

    list_display = ['cash_type', 'cash']


@admin.register(CashTake)
class CashTakeAdmin(admin.ModelAdmin):

    form = CashTakeForm
    date_hierarchy = 'take_date'
    list_display = ['take_date', 'cash_type', 'cash']


@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):

    form = PaymentTypeForm


@admin.register(ProductSell)
class ProductSellAdmin(admin.ModelAdmin):

    list_display = ['sell_date', 'seller']
    filter_horizontal = ['shipments', 'payments']
