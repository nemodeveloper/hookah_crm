from django.contrib import admin
from django.db.models import Sum

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
    list_filter = ['product_group__group_name']
    list_per_page = 50


@admin.register(ProductKind)
class ProductKindAdmin(admin.ModelAdmin):

    fieldsets = [
        (u'Информация по виду товара', {'fields': ['product_category', 'kind_name', 'min_count', 'need_update_products']})
    ]
    search_fields = ['kind_name']
    list_filter = ['product_category__category_name']
    list_display = ['kind_name', 'min_count', 'cur_count_product_by_kind', 'need_more_product_by_kind', 'need_update_products']
    list_per_page = 50
    ordering = ['kind_name']

    def cur_count_product_by_kind(self, obj):
        product_kind_count = Product.objects.filter(product_kind=obj).aggregate(Sum('product_count')).get('product_count__sum')
        return product_kind_count if product_kind_count else 0
    cur_count_product_by_kind.short_description = u'На складе(шт)'

    def need_more_product_by_kind(self, obj):
        product_kind_count = Product.objects.filter(product_kind=obj).aggregate(Sum('product_count')).get('product_count__sum')
        return obj.min_count > product_kind_count if product_kind_count else 0
    need_more_product_by_kind.boolean = True
    need_more_product_by_kind.short_description = u'Заканчивается'

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
    list_per_page = 50


class ProductKindFilter(admin.SimpleListFilter):

    title = u'Вид товара'
    parameter_name = u'product_kind__id__exact'

    def lookups(self, request, model_admin):
        category_id = request.GET.get('product_kind__product_category__id__exact')
        kinds = ProductKind.objects.filter(product_category=category_id) if category_id else ProductKind.objects.all()
        kinds.order_by('kind_name')

        return [(kind.id, kind.kind_name) for kind in kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{
                self.parameter_name: self.value()
            })
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    fieldsets = [
        (u'Информация по товару', {'fields': ['product_kind', 'product_name']}),
        (u'Внешний вид товара', {'fields': ['product_image']}),
        (u'Стоимость товара', {'fields': ['cost_price', 'price_retail', 'price_discount', 'price_wholesale', 'price_shop']})
    ]

    def get_list_display(self, request):
        base_list = ['product_kind', 'product_name', 'product_count']
        price_list = ['price_retail', 'price_discount', 'price_shop', 'price_wholesale', 'need_more_product']
        admin_list = ['cost_price']
        if request.user.is_superuser:
            price_list = admin_list + price_list
        return base_list + price_list

    ordering = ['product_name']
    list_filter = ['product_kind__product_category', ProductKindFilter]
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
    list_per_page = 50
    actions = None

    def format_invoice_date(self, obj):
        return obj.get_formatted_date()
    format_invoice_date.short_description = 'Дата поступления'

    def get_total_invoice_amount(self, obj):
        return obj.get_total_amount()
    get_total_invoice_amount.short_description = 'Сумма приемки'
