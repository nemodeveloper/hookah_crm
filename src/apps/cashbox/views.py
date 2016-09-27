from datetime import datetime

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import CreateView, FormView, DeleteView, TemplateView

from src.apps.cashbox.forms import ProductSellForm, ProductShipmentForm, PaymentTypeForm, CashTakeForm
from src.apps.cashbox.helper import ReportEmployerForPeriodProcessor, get_period, ProductSellReportForPeriod, PERIOD_KEY, \
    ProductSellCreditReport
from src.apps.cashbox.models import ProductSell, ProductShipment, PaymentType, CashTake, CashBox
from src.apps.cashbox.service import get_product_shipment_json, get_payment_type_json, update_cashbox_by_payments, \
    update_cashbox_by_cash_take, RollBackSellProcessor
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
        product_sell.sell_date = datetime.now()
        product_sell.save()

        shipments = str(form.cleaned_data['shipments']).split(',')
        payments = str(form.cleaned_data['payments']).split(',')

        product_sell.shipments.set(shipments)
        product_sell.payments.set(payments)
        product_sell.save()

        update_cashbox_by_payments(product_sell.payments.all())

        messages.success(self.request, 'Продажа успешно добавлена!')
        return HttpResponseRedirect('/admin/cashbox/productsell/')


class ProductSellDeleteView(AdminInMixin, DeleteView):

    def delete(self, request, *args, **kwargs):

        data = {
            'success': True,
        }

        if request.POST.get('rolllback_raw'):
            shipments = request.POST.get('shipments')
            shipments = shipments.split(',') if shipments else []

            payments = request.POST.get('payments')
            payments = payments.split(',') if payments else []

            RollBackSellProcessor.rollback_raw_sell(payments, shipments)

        elif kwargs.get('pk'):
            RollBackSellProcessor.rollback_sell(kwargs.get('pk'))
        else:
            data = {
                'success': False
            }
        return HttpResponse(build_json_from_dict(data), content_type='json')


class ProductSellView(ViewInMixin, TemplateView):

    template_name = 'cashbox/product_sell/view.html'

    def get_context_data(self, **kwargs):
        context = super(ProductSellView, self).get_context_data(**kwargs)
        context['product_sell'] = ProductSell.objects.get(pk=kwargs['pk'])
        return context


class ProductSellEmployerReport(ViewInMixin, TemplateView):

    template_name = 'cashbox/product_sell/employer_report.html'

    # TODO добавить проверку прав
    def get_context_data(self, **kwargs):
        context = super(ProductSellEmployerReport, self).get_context_data(**kwargs)
        period = get_period(self.request.GET.get(PERIOD_KEY), self.request.GET.get('period_start'), self.request.GET.get('period_end'))
        context['report'] = ReportEmployerForPeriodProcessor(kwargs['pk'], period[0], period[1])
        context['employer_id'] = kwargs['pk']
        return context


class ProductSellReport(ViewInMixin, TemplateView):

    template_name = 'cashbox/product_sell/report.html'

    def get_context_data(self, **kwargs):
        context = super(ProductSellReport, self).get_context_data(**kwargs)
        if self.request.user.id != int(kwargs['pk']):
            context['access_error'] = True
            return context

        period = get_period(self.request.GET.get(PERIOD_KEY), self.request.GET.get('period_start'),
                            self.request.GET.get('period_end'))
        context['report'] = ProductSellReportForPeriod(kwargs['pk'], period[0], period[1])

        return context


class ProductSellCreditReportView(ViewInMixin, TemplateView):

    template_name = 'cashbox/product_sell/credit_report.html'

    def get_context_data(self, **kwargs):
        context = super(ProductSellCreditReportView, self).get_context_data(**kwargs)
        period = get_period(self.request.GET.get(PERIOD_KEY), self.request.GET.get('period_start'),
                            self.request.GET.get('period_end'))
        context['report'] = ProductSellCreditReport(period[0], period[1])

        return context


class ProductShipmentCreate(AdminInMixin, CreateView):

    model = ProductShipment
    form_class = ProductShipmentForm

    def get_context_data(self, **kwargs):

        context = super(ProductShipmentCreate, self).get_context_data()
        return context

    @transaction.atomic
    def form_valid(self, form):

        if form.ajax_field_errors:
            return HttpResponse(build_json_from_dict(form.ajax_field_errors), content_type='json')

        product_shipment = form.save()
        update_storage(product_shipment.product, UPDATE_STORAGE_DEC_TYPE, product_shipment.product_count)

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
        update_storage(shipment.product, UPDATE_STORAGE_INC_TYPE, shipment.product_count)
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


class CashTakeCreateView(AdminInMixin, CreateView):

    model = CashTake
    form_class = CashTakeForm
    template_name = 'cashbox/cash_take/add.html'

    def get_success_url(self):
        return '/admin/cashbox/cashtake/'

    def get_context_data(self, **kwargs):
        context = super(CashTakeCreateView, self).get_context_data(**kwargs)
        context['cashboxs'] = CashBox.objects.all()
        return context

    def form_valid(self, form):

        cash_take = form.save(commit=False)
        cash_take.take_date = datetime.now()
        cash_take.save()

        update_cashbox_by_cash_take(cash_take)

        messages.success(self.request, 'Изъятие из кассы прошло успешно!')
        return HttpResponseRedirect(redirect_to=self.get_success_url())


class CashTakeView(ViewInMixin, TemplateView):

    template_name = 'cashbox/cash_take/view.html'

    def get_context_data(self, **kwargs):
        context = super(CashTakeView, self).get_context_data(**kwargs)
        context['cashtake'] = CashTake.objects.get(pk=kwargs['pk'])
        return context


