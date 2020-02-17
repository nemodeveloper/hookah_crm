import json
import operator
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, FormView, DeleteView, TemplateView
from django.views.generic import UpdateView
from django.views.generic.base import ContextMixin

from src.apps.cashbox import utils
from src.apps.cashbox.forms import ProductSellForm, ProductShipmentForm, PaymentTypeForm, \
    ProductSellUpdateForm
from src.apps.cashbox.helper import ReportEmployerForPeriodProcessor, get_period, ProductSellReportForPeriod, \
    PERIOD_KEY, \
    ProductSellCreditReport, ProductSellProfitReport, CustomerSellProfitReport
from src.apps.cashbox.models import ProductSell, ProductShipment, PaymentType
from src.apps.cashbox.operation import ProductSellCheckOperation, SellCustomerReportExcelOperation
from src.apps.cashbox.serializer import FakeProductShipment, FakePaymentType
from src.apps.cashbox.service import get_product_shipment_json, get_payment_type_json, RollBackSellProcessor
from src.apps.csa.csa_base import AdminInMixin, ViewInMixin, ExcelFileMixin
from src.apps.market.models import Customer, CustomerType
from src.base_components.views import LogViewMixin
from src.common_helper import build_json_from_dict


RETAIL_CUSTOMER = u'Розница'


class CashBoxLogViewMixin(LogViewMixin):

    def __init__(self):
        self.log_name = 'cashbox_log'
        super(CashBoxLogViewMixin, self).__init__()


def add_customer_data(context_date, with_retail_customer=True):
    customer_types = list(CustomerType.objects.order_by('type_name').all()) if with_retail_customer \
        else list(CustomerType.objects.exclude(type_name=RETAIL_CUSTOMER).order_by('type_name'))

    if with_retail_customer:
        # Розницу нужно показывать первой
        retail_customer_type = next((x for x in customer_types if x.type_name == RETAIL_CUSTOMER), None)
        if retail_customer_type:
            customer_types.remove(retail_customer_type)
            customer_types = [retail_customer_type] + customer_types

    context_date['customer_types'] = customer_types

    customers = Customer.objects.select_related('customer_type').all() if with_retail_customer \
        else Customer.objects.select_related('customer_type').exclude(name=RETAIL_CUSTOMER).all()

    customer_type_map_list = defaultdict(list)
    for customer in customers:
        customer_type_map_list[customer.customer_type.id].append(customer)
    customer_type_map_list = dict(customer_type_map_list)
    for customer_id, customer_list in customer_type_map_list.items():
        customer_type_map_list[customer_id] = sorted(customer_list, key=operator.attrgetter('name'))
    context_date['customer_type_map_list'] = customer_type_map_list


class ProductSellCreate(CashBoxLogViewMixin, AdminInMixin, CreateView):

    model = ProductSell
    form_class = ProductSellForm
    template_name = 'cashbox/product_sell/add.html'

    def get_context_data(self, **kwargs):
        context_date = super(ProductSellCreate, self).get_context_data(**kwargs)
        if self.request.method == 'GET':
            add_customer_data(context_date)

        return context_date

    @transaction.atomic
    def form_valid(self, form):

        product_sell = form.save(commit=False)
        product_sell.seller = self.request.user
        product_sell.customer_id = form.cleaned_data.get('customer_id')
        product_sell.sell_date = form.cleaned_data.get('sell_date') or timezone.now()
        product_sell.save()

        shipments = str(form.cleaned_data['shipments']).split(',')
        payments = str(form.cleaned_data['payments']).split(',')

        product_sell.shipments.set(list(ProductShipment.objects.filter(pk__in=shipments)))
        product_sell.payments.set(list(PaymentType.objects.filter(pk__in=payments)))

        product_sell.make_sell()

        self.log_info(message=product_sell.get_log_info())
        messages.success(self.request, 'Продажа успешно оформлена!')
        return HttpResponseRedirect('/admin/cashbox/productsell/')


class ProductSellDeleteView(CashBoxLogViewMixin, utils.ProductSellRestrictionMixin, AdminInMixin, DeleteView):

    def delete(self, request, *args, **kwargs):

        data = {
            'success': True,
        }

        processor = RollBackSellProcessor()

        if request.POST.get('rollback_raw'):
            shipments = request.POST.get('shipments')
            shipments = shipments.split(',') if shipments else []

            payments = request.POST.get('payments')
            payments = payments.split(',') if payments else []

            processor.rollback_raw_sell(payments, shipments)

        elif kwargs.get('pk'):
            processor.rollback_sell(kwargs.get('pk'))
            messages.info(request, message='Продажа успешно отменена!')
        else:
            data = {
                'success': False
            }

        return HttpResponse(build_json_from_dict(data), content_type='json')


class ProductSellUpdateView(utils.ProductSellRestrictionMixin, AdminInMixin, UpdateView):

    model = ProductSell
    form_class = ProductSellUpdateForm
    template_name = 'cashbox/product_sell/view.html'

    def get_context_data(self, **kwargs):
        context = super(ProductSellUpdateView, self).get_context_data(**kwargs)
        self.check_sell_owner(context['productsell'])
        return context

    def form_valid(self, form):
        response = super(ProductSellUpdateView, self).form_valid(form)
        messages.success(self.request, 'Время продажи успешно обновлено!')
        return response

    def get_success_url(self):
        return '/admin/cashbox/productsell/'

    def get_queryset(self):
        return ProductSell.objects\
            .select_related('seller', 'customer__customer_type')


# Получение чека по продаже
class ProductSellCheckView(AdminInMixin, ExcelFileMixin, View):

    def get(self, request, *args, **kwargs):
        operation = ProductSellCheckOperation(kwargs.get('id'))
        return self.build_response(operation.check_name, operation.get_excel_check())


class ProductSellEmployerReport(CashBoxLogViewMixin, ViewInMixin, TemplateView):

    template_name = 'cashbox/product_sell/employer_report.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(ProductSellEmployerReport, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductSellEmployerReport, self).get_context_data(**kwargs)
        empl_id = kwargs['pk']
        period = get_period(self.request.GET.get(PERIOD_KEY), self.request.GET.get('period_start'), self.request.GET.get('period_end'))
        context['report'] = ReportEmployerForPeriodProcessor(empl_id, period[0], period[1])
        context['employer_id'] = empl_id
        self.log_info(message='Пользователь %s, запросил отчет по работе сотрудника[id=%s]' % (self.request.user, empl_id))
        return context


class ProductSellReport(CashBoxLogViewMixin, ViewInMixin, TemplateView):

    template_name = 'cashbox/product_sell/report.html'

    def get_context_data(self, **kwargs):
        context = super(ProductSellReport, self).get_context_data(**kwargs)
        add_customer_data(context)

        period = get_period(self.request.GET.get(PERIOD_KEY), self.request.GET.get('period_start'),
                            self.request.GET.get('period_end'))
        raw_customer_ids = self.request.GET.get('customerIds')
        customer_ids = []
        if raw_customer_ids is not None and len(raw_customer_ids) > 0:
            customer_ids = raw_customer_ids.split(',')

        context['report'] = ProductSellReportForPeriod(period[0], period[1], customer_ids).process()

        self.log_info(message='Пользователь %s, запросил отчет по продажам!' % self.request.user)
        return context


class ProductSellCreditReportView(CashBoxLogViewMixin, ViewInMixin, TemplateView):

    template_name = 'cashbox/product_sell/credit_report.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(ProductSellCreditReportView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductSellCreditReportView, self).get_context_data(**kwargs)
        period = get_period(self.request.GET.get(PERIOD_KEY), self.request.GET.get('period_start'),
                            self.request.GET.get('period_end'))
        context['report'] = ProductSellCreditReport(period[0], period[1]).process()

        self.log_info(message='Пользователь %s, запросил отчет по задолникам!' % self.request.user)
        return context


class ProductSellProfitReportView(CashBoxLogViewMixin, ViewInMixin, TemplateView):

    template_name = 'cashbox/product_sell/profit_report.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(ProductSellProfitReportView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductSellProfitReportView, self).get_context_data(**kwargs)
        period = get_period(self.request.GET.get(PERIOD_KEY), self.request.GET.get('period_start'),
                            self.request.GET.get('period_end'))
        context['report'] = ProductSellProfitReport(period[0], period[1]).process()

        self.log_info(message='Пользователь %s, запросил отчет по прибыли!' % self.request.user)
        return context


class BaseProductSellCustomerReportView(AdminInMixin, CashBoxLogViewMixin, ContextMixin, ViewInMixin):

    def get_context_data(self, **kwargs):
        context = super(BaseProductSellCustomerReportView, self).get_context_data(**kwargs)
        add_customer_data(context)

        period = get_period(self.request.GET.get(PERIOD_KEY), self.request.GET.get('period_start'),
                            self.request.GET.get('period_end'))
        raw_product_kind_ids = self.request.GET.get('productKindIds')
        raw_customer_ids = self.request.GET.get('customerIds')
        product_kind_ids = []
        customer_ids = []
        if raw_product_kind_ids is not None and len(raw_product_kind_ids) > 0:
            product_kind_ids = raw_product_kind_ids.split(',')
        if raw_customer_ids is not None and len(raw_customer_ids) > 0:
            customer_ids = raw_customer_ids.split(',')

        context['report'] = CustomerSellProfitReport(period[0], period[1], product_kind_ids, customer_ids).process()

        self.log_info(message='Пользователь %s, запросил отчет по покупателям!' % self.request.user)
        return context


class ProductSellCustomerReportView(BaseProductSellCustomerReportView, TemplateView):

    template_name = 'cashbox/product_sell/profit_customer.html'


class ProductSellCustomerExcelReportView(BaseProductSellCustomerReportView, ExcelFileMixin, View):

    def get(self, request, *args, **kwargs):
        report = self.get_context_data(**kwargs)['report']
        operation = SellCustomerReportExcelOperation(report)
        return self.build_response(operation.file_name, operation.get_excel_file())


class ProductShipmentCreate(CashBoxLogViewMixin, AdminInMixin, CreateView):

    model = ProductShipment
    form_class = ProductShipmentForm

    def form_valid(self, form):

        if form.ajax_field_errors:
            return HttpResponse(build_json_from_dict(form.ajax_field_errors), content_type='json')

        with transaction.atomic():
            product_shipment = form.save(commit=False)
            product_shipment.initial_cost_price = product_shipment.cost_price
            product_shipment.product_cost_price = product_shipment.product.cost_price   # запоминаем себестоимость товара на момент продажи
            product_shipment.save()

        data = {
            'success': True,
            'shipment': FakeProductShipment(product_shipment)
        }

        self.log_info(message='Продавец %s, добавил партию товара для продажи - %s' % (self.request.user, product_shipment))
        return HttpResponse(build_json_from_dict(data), content_type='json')


class ProductShipmentUpdate(CashBoxLogViewMixin, AdminInMixin, UpdateView):

    model = ProductShipment
    form_class = ProductShipmentForm

    @staticmethod
    def update_shipment(old_shipment, new_shipment):
        old_count = old_shipment.product_count

        new_count = new_shipment.product_count
        new_cost = new_shipment.cost_price

        product = new_shipment.product

        total_count = old_count + new_count
        total_cost = new_cost

        new_shipment.cost_price = total_cost
        new_shipment.product_count = total_count
        new_shipment.product_cost_price = product.cost_price
        new_shipment.save()

    @transaction.atomic
    def form_valid(self, form):

        if form.ajax_field_errors:
            return HttpResponse(build_json_from_dict(form.ajax_field_errors), content_type='json')

        product_shipment = form.save(commit=False)
        old_product_shipment = ProductShipment.objects.get(pk=int(self.kwargs['pk']))
        self.update_shipment(old_product_shipment, product_shipment)

        data = {
            'success': True,
            'shipment': FakeProductShipment(product_shipment)
        }

        self.log_info(message='Пользователь %s, обновил партию товара для продажи - %s' % (self.request.user, product_shipment))
        return HttpResponse(build_json_from_dict(data), content_type='json')


class ProductShipmentJsonView(ViewInMixin, FormView):

    def get(self, request, *args, **kwargs):
        json_data = get_product_shipment_json(request.GET['id'])
        return HttpResponse(json_data, content_type='json')


class ProductShipmentDelete(CashBoxLogViewMixin, ViewInMixin, DeleteView):

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        shipment_id = request.POST.get('id')
        shipment = ProductShipment.objects.select_related('product').filter(id=shipment_id).first()

        if shipment:
            shipment.delete()
            self.log_info(message='Продавец %s, удалил партию товара с продажи - %s' % (self.request.user, shipment))
            result = {
                'success': True,
                'shipment': FakeProductShipment(shipment)
            }
        else:
            self.log_error(message='Продавец %s, не удалось найти партию товара для удаления из продажи по id=%s' % (self.request.user, shipment_id))
            result = {
                'success': False
            }

        return HttpResponse(build_json_from_dict(result), content_type='json')


class PaymentTypeCreate(CashBoxLogViewMixin, AdminInMixin, CreateView):

    model = PaymentType
    form_class = PaymentTypeForm
    template_name = 'cashbox/payment_type/add.html'

    def form_valid(self, form):
        if form.ajax_field_errors:
            return HttpResponse(build_json_from_dict(form.ajax_field_errors), content_type='json')

        payment = form.save()
        data = {
            'success': True,
            'payment': FakePaymentType(payment)
        }

        self.log_info(message='Пользователь %s, добавил оплату для продажи - %s' % (self.request.user, payment))
        return HttpResponse(build_json_from_dict(data), content_type='json')


class PaymentTypeDelete(CashBoxLogViewMixin, ViewInMixin, DeleteView):

    def delete(self, request, *args, **kwargs):
        payment = PaymentType.objects.get(id=request.POST.get('id'))
        payment.delete()
        self.log_info(message='Пользователь %s, удалил оплату от продажи - %s' % (self.request.user, payment))
        result = {'success': True}
        return HttpResponse(build_json_from_dict(result), content_type='json')


class PaymentTypeJsonView(ViewInMixin, FormView):

    def get(self, request, *args, **kwargs):
        json_data = get_payment_type_json(request.GET['id'])
        return HttpResponse(json_data, content_type='json')


