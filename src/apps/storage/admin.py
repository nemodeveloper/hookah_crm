from django.contrib import admin

from src.apps.storage.models import *


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):

    ordering = ['category_name']


@admin.register(ProductKind)
class ProductKindAdmin(admin.ModelAdmin):

    ordering = ['kind_name']


@admin.register(ProductProvider)
class ProductProviderAdmin(admin.ModelAdmin):

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
    list_filter = ['product_category', 'product_kind']
    search_fields = ['product_name']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    fieldsets = [
        (u'Информация по накладной', {'fields': ['invoice_date', 'product_provider', 'overhead']}),
        (u'Товары', {'fields': ['shipments']})
    ]
    filter_horizontal = ['shipments']
    ordering = ['invoice_date']


@admin.register(ProductStorage)
class ProductStorageAdmin(admin.ModelAdmin):

    list_display = ['product', 'product_count']

