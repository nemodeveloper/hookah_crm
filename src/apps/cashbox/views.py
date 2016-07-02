from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import CreateView, FormView, DeleteView

from src.apps.cashbox.forms import ProductSellForm, ProductShipmentForm, PaymentTypeForm
from src.apps.cashbox.models import ProductSell, ProductShipment, PaymentType
from src.apps.cashbox.service import get_product_shipment_json, get_payment_type_json, update_cashbox_by_payments
from src.apps.csa.csa_base import AdminInMixin, ViewInMixin
from src.apps.storage.service import update_storage, UPDATE_STORAGE_DEC_TYPE, UPDATE_STORAGE_INC_TYPE
from src.common_helper import build_json_from_dict


class ProductSellCreate(AdminInMixin, CreateView):

    model = ProductSell
    form_class = ProductSellForm
    template_name = 'cashbox/product_sell/add.html'

    @transaction.atomic
    def form_valid(self, form):

        product_sell = form.save(commit=False)
        product_sell.seller = self.request.user
        product_sell.save()

        shipments = str(form.cleaned_data['shipments']).split(',')
        payments = str(form.cleaned_data['payments']).split(',')

        product_sell.shipments.set(shipments)
        product_sell.payments.set(payments)
        product_sell.save()

        update_cashbox_by_payments(product_sell.payments.all())

        return HttpResponseRedirect('/admin/cashbox/productsell/')


class ProductShipmentCreate(AdminInMixin, CreateView):

    model = ProductShipment
    form_class = ProductShipmentForm
    template_name = 'cashbox/product_shipment/add.html'

    def get_context_data(self, **kwargs):

        context = super(ProductShipmentCreate, self).get_context_data()
        return context

    @transaction.atomic
    def form_valid(self, form):

        if form.ajax_field_errors:
            return HttpResponse(build_json_from_dict(form.ajax_field_errors), content_type='json')

        product_shipment = form.save()
        update_storage(product_shipment.product.id, UPDATE_STORAGE_DEC_TYPE, product_shipment.product_count)

        data = {
            'success': True,
            'id': product_shipment.id
        }

        return HttpResponse(build_json_from_dict(data), content_type='json')


class ProductShipmentJsonView(ViewInMixin, FormView):

    def get(self, request, *args, **kwargs):

        json_data = get_product_shipment_json(request.GET['id'])
        return HttpResponse(json_data, content_type='json')


class ProductShipmentDelete(ViewInMixin, DeleteView):

    @transaction.atomic
    def delete(self, request, *args, **kwargs):

        shipment_id = request.POST.get('id')
        shipment = ProductShipment.objects.get(id=shipment_id)
        update_storage(shipment.product.id, UPDATE_STORAGE_INC_TYPE, shipment.product_count)
        shipment.delete()

        result = {'success': True}
        return HttpResponse(build_json_from_dict(result), content_type='json')


class PaymentTypeCreate(AdminInMixin, CreateView):

    model = PaymentType
    form_class = PaymentTypeForm
    template_name = 'cashbox/payment_type/add.html'

    def get_context_data(self, **kwargs):

        context = super(PaymentTypeCreate, self).get_context_data()
        return context

    def form_valid(self, form):

        if form.ajax_field_errors:
            return HttpResponse(build_json_from_dict(form.ajax_field_errors), content_type='json')

        payment_type = form.save()
        data = {
            'success': True,
            'id': payment_type.id
        }

        return HttpResponse(build_json_from_dict(data), content_type='json')


class PaymentTypeDelete(ViewInMixin, DeleteView):

    def delete(self, request, *args, **kwargs):

        payment_type_id = request.POST.get('id')
        PaymentType.objects.filter(id=payment_type_id).first().delete()
        result = {'success': True}
        return HttpResponse(build_json_from_dict(result), content_type='json')


class PaymentTypeJsonView(ViewInMixin, FormView):

    def get(self, request, *args, **kwargs):

        json_data = get_payment_type_json(request.GET['id'])
        return HttpResponse(json_data, content_type='json')
