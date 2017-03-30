from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import F
from django.db.models import Sum

from src.apps.storage.forms import ProductProviderAdminForm
from src.apps.storage.models import *


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):

    list_display = ['group_name', 'cost_product_by_group']
    search_fields = ['group_name']
    list_per_page = 50

    def cost_product_by_group(self, obj):
        product_group_cost = Product.objects.filter(product_kind__product_category__product_group=obj).aggregate(total=Sum(F('cost_price') * F('product_count'), output_field=models.DecimalField(decimal_places=2)))['total']
        return intcomma(product_group_cost) if product_group_cost else 0
    cost_product_by_group.short_description = u'Сумма товара'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):

    list_display = ['category_name', 'cost_product_by_category']
    ordering = ['category_name']
    search_fields = ['category_name']
    list_filter = ['product_group__group_name']
    list_per_page = 50

    def cost_product_by_category(self, obj):
        product_category_cost = Product.objects.filter(product_kind__product_category=obj).aggregate(total=Sum(F('cost_price') * F('product_count'), output_field=models.DecimalField(decimal_places=2)))['total']
        return intcomma(product_category_cost) if product_category_cost else 0
    cost_product_by_category.short_description = u'Сумма товара'


@admin.register(ProductKind)
class ProductKindAdmin(admin.ModelAdmin):

    fieldsets = [
        (u'Информация по виду товара', {'fields': ['product_category', 'kind_name', 'min_count', 'need_update_products']})
    ]
    search_fields = ['kind_name']
    list_filter = ['product_category__category_name']
    list_display = ['kind_name', 'min_count', 'cur_count_product_by_kind', 'cur_cost_product_by_kind', 'need_more_product_by_kind', 'need_update_products']
    list_per_page = 50
    show_full_result_count = False
    ordering = ['kind_name']

    def cur_count_product_by_kind(self, obj):
        product_kind_count = Product.objects.filter(product_kind=obj).aggregate(Sum('product_count')).get('product_count__sum')
        return product_kind_count if product_kind_count else 0
    cur_count_product_by_kind.short_description = u'На складе(шт)'

    def cur_cost_product_by_kind(self, obj):
        product_kind_cost = Product.objects.filter(product_kind=obj).aggregate(total=Sum(F('cost_price') * F('product_count'), output_field=models.DecimalField(decimal_places=2)))['total']
        return intcomma(product_kind_cost) if product_kind_cost else 0
    cur_cost_product_by_kind.short_description = u'Сумма товара'

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


class ProductCategoryFilter(admin.SimpleListFilter):

    title = u'Категория товара'
    parameter_name = 'product_kind__product_category__id__exact'

    def lookups(self, request, model_admin):
        categories = ProductCategory.objects.all().order_by('category_name')
        return [(category.id, category.category_name) for category in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{
                self.parameter_name: self.value()
            })
        return queryset


class ProductKindFilter(admin.SimpleListFilter):

    title = u'Вид товара'
    parameter_name = 'product_kind__id__exact'

    def lookups(self, request, model_admin):
        category_id = request.GET.get('product_kind__product_category__id__exact')
        kinds = ProductKind.objects.filter(product_category_id=category_id).order_by('kind_name') \
            if category_id else ProductKind.objects.all().order_by('kind_name')

        return [(kind.id, kind.kind_name) for kind in kinds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{
                self.parameter_name: self.value()
            })
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    def lookup_allowed(self, lookup, value):
        if lookup in ('product_kind__product_category__id__exact', 'product_kind__id__exact'):
            return True
        return super(ProductAdmin, self).lookup_allowed(lookup, value)

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

    ordering = ['product_kind__kind_name', 'product_name']
    list_filter = [ProductCategoryFilter, ProductKindFilter]
    search_fields = ['product_name']
    list_per_page = 50
    show_full_result_count = False

    def need_more_product(self, obj):
        return obj.min_count > obj.product_count
    need_more_product.boolean = True
    need_more_product.short_description = u'Заканчивается'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = ['format_invoice_date', 'owner', 'get_total_invoice_amount', 'overhead', 'status', 'product_provider']
    ordering = ['-status', '-invoice_date']
    date_hierarchy = 'invoice_date'
    list_per_page = 20
    actions = None

    def format_invoice_date(self, obj):
        return obj.get_formatted_date()
    format_invoice_date.short_description = 'Дата поступления'

    def get_total_invoice_amount(self, obj):
        return obj.get_total_amount()
    get_total_invoice_amount.short_description = 'Сумма приемки'


@admin.register(Revise)
class ReviseAdmin(admin.ModelAdmin):

    list_display = ['owner', 'format_revise_date', 'status']
    ordering = ['-revise_date']
    date_hierarchy = 'revise_date'
    list_per_page = 20
    actions = None

    def format_revise_date(self, obj):
        return obj.get_verbose_revise_date()
    format_revise_date.short_description = 'Дата сверки'
