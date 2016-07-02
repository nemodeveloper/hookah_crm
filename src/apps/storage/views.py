from django.db import transaction
from django.http import HttpResponse

# Create your views here.
from django.views.generic import FormView, CreateView, DeleteView

from src.apps.csa.csa_base import ViewInMixin, AdminInMixin
from src.apps.storage.forms import InvoiceForm, ShipmentForm
from src.apps.storage.models import Invoice, Shipment, ProductProvider
from src.apps.storage.service import get_products_all_json, get_products_balance_json, get_shipment_json, \
    update_storage_by_shipments
from src.common_helper import build_json_from_dict


class ProductJsonView(ViewInMixin, FormView):

    def get(self, request, *args, **kwargs):

        json_data = {}
        if request.GET['product_list'] == 'all':
            json_data = get_products_all_json()
        elif request.GET['product_list'] == 'balance':
            json_data = get_products_balance_json()

        return HttpResponse(json_data, content_type='json')


class InvoiceCreate(AdminInMixin, CreateView):

    model = Invoice
    form_class = InvoiceForm
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
        invoice.owner = self.request.user
        invoice.save()

        shipments = str(form.cleaned_data['shipments']).split(',')

        invoice.shipments.set(shipments)
        invoice.save()

        update_storage_by_shipments(invoice.shipments.all())

        data = {
            'success': True,
            'id': invoice.id
        }

        return HttpResponse(build_json_from_dict(data), content_type='json')


class ShipmentCreate(AdminInMixin, CreateView):

    model = Shipment
    form_class = ShipmentForm
    template_name = 'storage/shipment/add.html'

    @transaction.atomic
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
