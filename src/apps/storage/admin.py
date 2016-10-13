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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    fieldsets = [
        (u'Информация по товару', {'fields': ['product_kind', 'product_name']}),
        (u'Внешний вид товара', {'fields': ['product_image']}),
        (u'Стоимость товара', {'fields': ['cost_price', 'price_retail', 'price_discount', 'price_wholesale', 'price_shop']})
    ]
    list_display = ['product_kind', 'product_name', 'get_storage_count', 'cost_price', 'price_retail', 'price_discount', 'price_shop', 'price_wholesale']
    ordering = ['product_name']
    list_filter = ['product_kind__product_category', 'product_kind']
    search_fields = ['product_name']
    list_per_page = 50

    def get_storage_count(self, obj):
        return obj.get_storage_count()
    get_storage_count.short_description = u'На складе(шт)'


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
    list_display = ['product', 'product_count', 'get_cost_price', 'get_retail_price', 'get_discount_price', 'get_wholesale_price', 'get_shop_price', 'check_balance']
    list_filter = ['product__product_kind__product_category', 'product__product_kind']
    search_fields = ['product__product_name']
    ordering = ['product__product_name']
    list_per_page = 50

    def check_balance(self, obj):
        return obj.min_count > obj.product_count
    check_balance.boolean = True
    check_balance.short_description = u'Необходимо пополнение'

    def get_cost_price(self, obj):
        return obj.product.cost_price
    get_cost_price.short_description = u'Себестоимость'

    def get_retail_price(self, obj):
        return obj.product.price_retail
    get_retail_price.short_description = u'Розница'

    def get_discount_price(self, obj):
        return obj.product.price_discount
    get_discount_price.short_description = u'Дисконт'

    def get_shop_price(self, obj):
        return obj.product.price_shop
    get_shop_price.short_description = u'Магазины'

    def get_wholesale_price(self, obj):
        return obj.product.price_wholesale
    get_wholesale_price.short_description = u'Оптом'