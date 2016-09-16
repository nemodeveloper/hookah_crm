from datetime import datetime

from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response

from django.views.generic import FormView, CreateView, DeleteView, UpdateView, TemplateView

from src.apps.csa.csa_base import ViewInMixin, AdminInMixin
from src.apps.storage.forms import InvoiceAddForm, ShipmentForm, ProductForm, ProductStorageForm
from src.apps.storage.helper import ProductStorageExcelProcessor, InvoiceMonthReportProcessor
from src.apps.storage.models import Invoice, Shipment, ProductProvider, Product, ProductStorage
from src.apps.storage.service import get_products_all_json, get_products_balance_json, get_shipment_json, \
    get_kinds_for_product_add_json, StorageProductUpdater
from src.common_helper import build_json_from_dict
from src.form_components.base_form import UploadFileForm


class ProductAddView(AdminInMixin, CreateView):

    model = Product
    form_class = ProductForm
    template_name = 'storage/product/add.html'

    def get_context_data(self, **kwargs):

        context = super(ProductAddView, self).get_context_data(**kwargs)
        context['form_type'] = 'add'

        return context

    def get_success_url(self):
        return '/admin/storage/product/'


class ProductUpdateView(AdminInMixin, UpdateView):

    model = Product
    form_class = ProductForm
    template_name = 'storage/product/add.html'

    def get_context_data(self, **kwargs):

        context = super(ProductUpdateView, self).get_context_data(**kwargs)
        context['form_type'] = 'edit'

        return context

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

        return HttpResponse(json_data, content_type='json')


class ProductStorageCreateView(AdminInMixin, CreateView):

    model = ProductStorage
    form_class = ProductStorageForm
    template_name = 'storage/productstorage/add.html'

    def get_success_url(self):
        return '/admin/storage/productstorage/'


class InvoiceCreate(AdminInMixin, CreateView):

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

        return HttpResponse(build_json_from_dict(data), content_type='json')


class InvoiceBuyReport(ViewInMixin, TemplateView):

    template_name = 'storage/invoice/invoice_report.html'

    # TODO добавить проверку прав
    def get_context_data(self, **kwargs):
        context = super(InvoiceBuyReport, self).get_context_data(**kwargs)
        context['report'] = InvoiceMonthReportProcessor(datetime.now())
        return context


class InvoiceView(AdminInMixin, TemplateView):

    template_name = 'storage/invoice/view.html'

    def get_context_data(self, **kwargs):

        context = super(InvoiceView, self).get_context_data(**kwargs)
        context['invoice'] = Invoice.objects.get(id=self.kwargs['pk'])
        return context


class ShipmentCreate(AdminInMixin, CreateView):

    model = Shipment
    form_class = ShipmentForm

    def form_valid(self, form):

        if form.ajax_field_errors:
            return HttpResponse(build_json_from_dict(form.ajax_field_errors), content_type='json')

        product_shipment = form.save()
        data = {
            'success': True,
            'id': product_shipment.id
        }

        return HttpResponse(build_json_from_dict(data), content_type='json')


class ShipmentDelete(ViewInMixin, DeleteView):

    @transaction.atomic
    def delete(self, request, *args, **kwargs):

        shipment_id = request.POST.get('id')
        shipment = Shipment.objects.get(id=shipment_id)
        shipment.delete()

        result = {'success': True}
        return HttpResponse(build_json_from_dict(result), content_type='json')


class ShipmentJsonView(ViewInMixin, FormView):

    def get(self, request, *args, **kwargs):

        json_data = get_shipment_json(request.GET['id'])
        return HttpResponse(json_data, content_type='json')


class ImportProductStorageView(AdminInMixin, FormView):

    form_class = UploadFileForm
    template_name = 'storage/productstorage/import.html'

    def form_valid(self, form):
        file_processor = ProductStorageExcelProcessor(form.cleaned_data.get('file'))
        file_processor.process()
        errors = file_processor.get_errors()
        return render_to_response('storage/productstorage/import_result.html',
                                  context={'errors': errors})


