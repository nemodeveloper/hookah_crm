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
    fieldsets = [
        (u'Информация по виду товара', {'fields': ['product_category', 'kind_name', 'need_update_products']})
    ]
    list_display = ['kind_name', 'need_update_products']
    list_per_page = 50

    def update_products_cost(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            ProductKind.objects.filter(id__in=selected).update(need_update_products=True)
        else:
            self.message_user(request, "Для обновления необходимо выбрать минимум 1 вид товара!")
    update_products_cost.short_description = "Обновлять стоимость при приемке"

    def not_update_products_cost(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            ProductKind.objects.filter(id__in=selected).update(need_update_products=False)
        else:
            self.message_user(request, "Для обновления необходимо выбрать минимум 1 вид товара!")
    not_update_products_cost.short_description = "Не обновлять стоимость при приемке"

    actions = [update_products_cost, not_update_products_cost]


@admin.register(ProductProvider)
class ProductProviderAdmin(admin.ModelAdmin):

    form = ProductProviderAdminForm
    fieldsets = [
        (u'Информация по поставщику', {'fields': ['provider_name', 'description']})
    ]
    list_display = ['provider_name', 'description']
    ordering = ['provider_name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    fieldsets = [
        (u'Информация по товару', {'fields': ['product_kind', 'product_name']}),
        (u'Внешний вид товара', {'fields': ['product_image']}),
        (u'Стоимость товара', {'fields': ['cost_price', 'price_retail', 'price_discount', 'price_wholesale', 'price_shop']})
    ]
    list_display = ['product_kind', 'product_name', 'product_count', 'cost_price', 'price_retail', 'price_discount', 'price_shop', 'price_wholesale', 'need_more_product']
    ordering = ['product_name']
    list_filter = ['product_kind__product_category', 'product_kind']
    search_fields = ['product_name']
    list_per_page = 50

    def need_more_product(self, obj):
        return obj.min_count > obj.product_count
    need_more_product.boolean = True
    need_more_product.short_description = u'Заканчивается'


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