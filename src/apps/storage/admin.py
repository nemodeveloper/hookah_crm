from django.contrib import admin

from src.apps.storage.forms import ProductProviderAdminForm
from src.apps.storage.models import *


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):

    ordering = ['category_name']
    search_fields = ['category_name']
    list_per_page = 20


@admin.register(ProductKind)
class ProductKindAdmin(admin.ModelAdmin):

    ordering = ['kind_name']
    search_fields = ['kind_name']
    list_per_page = 20


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
        (u'Информация по товару', {'fields': ['product_category', 'product_kind', 'product_name']}),
        (u'Внешний вид товара', {'fields': ['product_image']}),
        (u'Стоимость товара', {'fields': ['cost_price', 'price_retail', 'price_discount', 'price_wholesale']})
    ]
    list_display = ['product_name', 'cost_price', 'price_retail', 'price_discount', 'price_wholesale']
    ordering = ['product_name']
    list_filter = [
        ('product_category', admin.RelatedOnlyFieldListFilter),
        ('product_kind', admin.RelatedOnlyFieldListFilter)
    ]
    search_fields = ['product_name']
    list_per_page = 20


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    fieldsets = [
        (u'Информация по накладной', {'fields': ['invoice_date', 'product_provider', 'overhead']}),
        (u'Товары', {'fields': ['shipments']})
    ]
    list_display = ['invoice_date', 'product_provider']
    filter_horizontal = ['shipments']
    ordering = ['invoice_date']
    date_hierarchy = 'invoice_date'
    list_per_page = 20


@admin.register(ProductStorage)
class ProductStorageAdmin(admin.ModelAdmin):

    list_display = ['product', 'product_count', 'min_count', 'check_balance']
    list_filter = ['product__product_category', 'product__product_kind']
    search_fields = ['product__product_name']
    ordering = ['product__product_name']
    list_per_page = 20

    def check_balance(self, obj):
        return obj.min_count > obj.product_count
    check_balance.boolean = True
    check_balance.short_description = u'Необходимо пополнение'

