from django.contrib import admin

from src.apps.storage.forms import ProductProviderAdminForm
from src.apps.storage.models import *


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):

    search_fields = ['group_name']
    list_per_page = 50


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):

    ordering = ['category_name']
    search_fields = ['category_name']
    list_per_page = 50


@admin.register(ProductKind)
class ProductKindAdmin(admin.ModelAdmin):

    ordering = ['kind_name']
    search_fields = ['kind_name']
    list_per_page = 50


@admin.register(ProductProvider)
class ProductProviderAdmin(admin.ModelAdmin):

    form = ProductProviderAdminForm
    fieldsets = [
        (u'Информация по поставщику', {'fields': ['provider_name', 'description']})
    ]
    list_display = ['provider_name', 'description']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    fieldsets = [
        (u'Информация по товару', {'fields': ['product_kind', 'product_name', 'product_code']}),
        (u'Внешний вид товара', {'fields': ['product_image']}),
        (u'Стоимость товара', {'fields': ['cost_price', 'price_retail', 'price_discount', 'price_shop', 'price_wholesale']})
    ]
    list_display = ['product_kind', 'product_name', 'cost_price', 'price_retail', 'price_discount', 'price_shop', 'price_wholesale']
    ordering = ['product_name']
    list_filter = ['product_kind__product_category', 'product_kind']
    search_fields = ['product_name', 'product_code']
    list_per_page = 50


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = ['format_invoice_date', 'owner', 'get_total_invoice_amount', 'overhead', 'product_provider']
    ordering = ['-invoice_date']
    date_hierarchy = 'invoice_date'
    list_per_page = 20
    actions = None

    def format_invoice_date(self, obj):
        return obj.get_formatted_date()
    format_invoice_date.short_description = 'Дата поступления'

    def get_total_invoice_amount(self, obj):
        return obj.get_total_amount()
    get_total_invoice_amount.short_description = 'Сумма приемки'


@admin.register(ProductStorage)
class ProductStorageAdmin(admin.ModelAdmin):

    fieldsets = [
        (u'Информация по товару на складе', {'fields': ['product', 'product_count', 'min_count']})
    ]
    readonly_fields = ['product']
    list_display = ['product', 'product_count', 'min_count', 'check_balance']
    list_filter = ['product__product_kind__product_category', 'product__product_kind']
    search_fields = ['product__product_name', 'product__product_code']
    ordering = ['product__product_name']
    list_per_page = 50

    def check_balance(self, obj):
        return obj.min_count > obj.product_count
    check_balance.boolean = True
    check_balance.short_description = u'Необходимо пополнение'

