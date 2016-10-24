from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator

from django.views.generic import FormView, CreateView, DeleteView, UpdateView, TemplateView
from openpyxl.writer.excel import save_virtual_workbook

from src.apps.cashbox.helper import PERIOD_KEY
from src.apps.cashbox.helper import get_period
from src.apps.cashbox.serializer import FakeProductShipment
from src.apps.csa.csa_base import ViewInMixin, AdminInMixin
from src.apps.storage.forms import InvoiceAddForm, ShipmentForm, ProductForm, ExportProductForm
from src.apps.storage.helper import ProductExcelProcessor, InvoiceReportProcessor, \
    ExportProductProcessor
from src.apps.storage.models import Invoice, Shipment, ProductProvider, Product
from src.apps.storage.service import get_products_all_json, get_products_balance_json, get_shipment_json, \
    get_kinds_for_product_add_json, StorageProductUpdater, update_all_product_cost_by_kind, get_kinds_for_export_json
from src.base_components.views import LogViewMixin
from src.common_helper import build_json_from_dict
from src.base_components.form_components.base_form import UploadFileForm
from src.template_tags.common_tags import format_date


class StorageLogViewMixin(LogViewMixin):

    def __init__(self):
        self.log_name = 'storage_log'
        super(StorageLogViewMixin, self).__init__()


class ProductAddViewMixin(StorageLogViewMixin, AdminInMixin, CreateView):

    model = Product
    form_class = ProductForm
    template_name = 'storage/product/add.html'

    def get_context_data(self, **kwargs):

        context = super(ProductAddViewMixin, self).get_context_data(**kwargs)
        context['form_type'] = 'add'

        return context

    def form_valid(self, form):
        response = super(ProductAddViewMixin, self).form_valid(form)
        messages.success(self.request, 'Товар %s успешно добавлен!' % form.instance.product_name)
        self.log_info('Пользователь %s, добавил продукт - %s' % (self.request.user, form.instance))
        return response

    def get_success_url(self):
        return reverse('product_add')


class ProductUpdateViewMixin(StorageLogViewMixin, AdminInMixin, UpdateView):

    model = Product
    form_class = ProductForm
    template_name = 'storage/product/add.html'

    def get_template_names(self):
        return self.template_name if self.request.user.is_superuser else 'storage/product/view.html'

    def get_context_data(self, **kwargs):
        context = super(ProductUpdateViewMixin, self).get_context_data(**kwargs)
        context['form_type'] = 'edit'

        product = Product.objects.select_related().get(id=self.kwargs.get('pk'))
        context['product_kind_id'] = product.product_kind.id

        if not self.request.user.is_superuser:
            context['product_group'] = product.product_kind.product_category.product_group.group_name
            context['product_category'] = product.product_kind.product_category.category_name
            context['product_kind'] = product.product_kind.kind_name
            context['form_type'] = 'view'

        return context

    def form_valid(self, form):
        response = super(ProductUpdateViewMixin, self).form_valid(form)
        if form.cleaned_data.get('update_kind'):
            update_all_product_cost_by_kind(form.instance)
        self.log_info('Пользователь %s, обновил продукт id = %s, %s' % (self.request.user, form.instance.id, form.instance))

        return response

    def get_success_url(self):
        return '/admin/storage/product/'


class ProductJsonView(ViewInMixin, FormView):

    def get(self, request, *args, **kwargs):

        json_data = {}
        if request.GET['product_list'] == 'all':
            json_data = get_products_all_json()
        elif request.GET['product_list'] == 'balance':
            json_data = get_products_balance_json()
        elif request.GET['product_list'] == 'product_add':
            json_data = get_kinds_for_product_add_json()
        elif request.GET['product_list'] == 'balance_kinds':
            json_data = get_kinds_for_export_json()

        return HttpResponse(json_data, content_type='json')


class InvoiceCreate(StorageLogViewMixin, AdminInMixin, CreateView):

    model = Invoice
    form_class = InvoiceAddForm
    template_name = 'storage/invoice/add.html'

    def get_context_data(self, **kwargs):

        data = super(InvoiceCreate, self).get_context_data(**kwargs)
        data['providers'] = ProductProvider.objects.all()

        return data

    @transaction.atomic
    def form_valid(self, form):

        if form.ajax_field_errors:
            return HttpResponse(build_json_from_dict(form.ajax_field_errors), content_type='json')

        invoice = form.save(commit=False)
        invoice.invoice_date = timezone.now()
        invoice.owner = self.request.user
        invoice.save()

        shipments = str(form.cleaned_data['shipments']).split(',')

        invoice.shipments.set(shipments)
        invoice.save()

        product_updater = StorageProductUpdater(invoice.shipments.all())
        product_updater.update()

        data = {
            'success': True,
            'id': invoice.id
        }

        self.log_info('Пользователь %s, добавил приемку товара - %s' % (self.request.user, form.instance))
        return HttpResponse(build_json_from_dict(data), content_type='json')


class InvoiceBuyReport(StorageLogViewMixin, ViewInMixin, TemplateView):

    template_name = 'storage/invoice/invoice_report.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(InvoiceBuyReport, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InvoiceBuyReport, self).get_context_data(**kwargs)
        period = get_period(self.request.GET.get(PERIOD_KEY), self.request.GET.get('period_start'),
                            self.request.GET.get('period_end'))
        context['report'] = InvoiceReportProcessor(period[0], period[1])
        self.log_info('Пользователь %s, запросил отчет по приемке товара с %s по %s' % (self.request.user, format_date(period[0]), format_date(period[1])))
        return context


class InvoiceView(AdminInMixin, TemplateView):

    template_name = 'storage/invoice/view.html'

    def get_context_data(self, **kwargs):

        context = super(InvoiceView, self).get_context_data(**kwargs)
        context['invoice'] = Invoice.objects.get(id=self.kwargs['pk'])
        return context


class ShipmentCreate(StorageLogViewMixin, AdminInMixin, CreateView):

    model = Shipment
    form_class = ShipmentForm

    def form_valid(self, form):

        if form.ajax_field_errors:
            return HttpResponse(build_json_from_dict(form.ajax_field_errors), content_type='json')

        product_shipment = form.save()
        data = {
            'success': True,
            'shipment': FakeProductShipment(product_shipment)
        }

        self.log_info('Пользователь %s, добавил сырую поставку товара для приемки %s' % (self.request.user, form.instance))
        return HttpResponse(build_json_from_dict(data), content_type='json')


class ShipmentDelete(StorageLogViewMixin, ViewInMixin, DeleteView):

    def delete(self, request, *args, **kwargs):

        shipment_id = request.POST.get('id')
        shipment = Shipment.objects.get(id=shipment_id)
        self.log_info('Пользователь %s, удалил сырую поставку товара для приемки %s' % (self.request.user, shipment))
        shipment.delete()

        result = {'success': True}
        return HttpResponse(build_json_from_dict(result), content_type='json')


class ShipmentJsonView(ViewInMixin, FormView):

    def get(self, request, *args, **kwargs):

        json_data = get_shipment_json(request.GET['id'])
        return HttpResponse(json_data, content_type='json')


class ImportProductViewMixin(StorageLogViewMixin, AdminInMixin, FormView):

    form_class = UploadFileForm
    template_name = 'storage/product/import.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(ImportProductViewMixin, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        file_processor = ProductExcelProcessor(form.cleaned_data.get('file'))
        file_processor.process()
        errors = file_processor.get_errors()
        self.log_info('Пользователь %s, инициировал загрузку товара на склад!' % self.request.user)
        return render_to_response('storage/product/import_result.html',
                                  context={'errors': errors})


class ExportProductViewMixin(StorageLogViewMixin, AdminInMixin, FormView):

    template_name = 'storage/product/export.html'
    form_class = ExportProductForm

    @staticmethod
    def build_response(book):
        response = HttpResponse(save_virtual_workbook(book),
                                content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=StorageProducts.xlsx'
        return response

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('export_type'):
            if not request.user.is_superuser:
                return HttpResponseForbidden()
            export_type = self.request.GET.get('export_type')
            export_processor = ExportProductProcessor(export_type=export_type)
            book = export_processor.generate_storage_file()
            self.log_info('Пользователь %s, запросил полную выгрузку остатков товара со склада!' % self.request.user)
            return self.build_response(book)
        else:
            return super(ExportProductViewMixin, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        kinds = form.cleaned_data.get('kinds').split(',')
        export_processor = ExportProductProcessor(kinds)
        book = export_processor.generate_storage_file()

        self.log_info('Пользователь %s, запросил выгрузку остатков товара со склада!' % self.request.user)
        return self.build_response(book)



