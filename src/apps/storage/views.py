
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from django.views.generic import FormView, CreateView, DeleteView, UpdateView, TemplateView
from openpyxl.writer.excel import save_virtual_workbook

from src.apps.cashbox.helper import PERIOD_KEY
from src.apps.cashbox.helper import get_period
from src.apps.cashbox.serializer import FakeProductShipment
from src.apps.csa.csa_base import ViewInMixin, AdminInMixin, ExcelFileMixin
from src.apps.storage.forms import InvoiceAddForm, ShipmentForm, ProductForm, ExportProductForm, InvoiceUpdateForm, \
    ProductKindForm
from src.apps.storage.helper import ProductExcelProcessor, InvoiceReportProcessor, \
    ExportProductProcessor, ReviseProductExcelProcessor
from src.apps.storage.models import Invoice, Shipment, ProductProvider, Product, STORAGE_PERMS, Revise, ProductRevise, \
    ProductKind, ProductCategory
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

        # Обновим вид товара для фильтра
        if self.request.session.get('product_kind_id'):
            context['product_kind_id'] = self.request.session['product_kind_id']

        return context

    def form_valid(self, form):
        response = super(ProductAddViewMixin, self).form_valid(form)
        messages.success(self.request, 'Товар %s успешно добавлен!' % form.instance.product_name)
        self.request.session['product_kind_id'] = form.instance.product_kind_id
        self.log_info('Пользователь %s, добавил продукт - %s' % (self.request.user, form.instance))
        return response

    def get_success_url(self):
        return reverse('product_add')


class ProductUpdateViewMixin(StorageLogViewMixin, AdminInMixin, UpdateView):

    model = Product
    form_class = ProductForm
    template_name = 'storage/product/add.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            if request.user.has_perm(STORAGE_PERMS.get('view_product')):
                return HttpResponseRedirect(redirect_to=reverse('product_view', args=args, kwargs=kwargs))
            else:
                raise HttpResponseForbidden()
        return super(ProductUpdateViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductUpdateViewMixin, self).get_context_data(**kwargs)

        context['form_type'] = 'edit'
        context['product_kind_id'] = self.object.product_kind_id

        return context

    def form_valid(self, form):
        self.log_info('Пользователь %s, инициировал обновление товара:\n'
                      'Редактируемые поля - %s\n'
                      'Поля товара до обновления - %s' %
                      (self.request.user, form.changed_data, form.initial))
        response = super(ProductUpdateViewMixin, self).form_valid(form)
        if form.cleaned_data.get('update_kind'):
            update_all_product_cost_by_kind(form.instance)
        self.log_info('Пользователь %s, обновил товар id = %s, %s\n'
                      'Поля товара после обновления %s'
                      % (self.request.user, form.instance.id, form.instance, form.cleaned_data))

        return response

    def get_success_url(self):
        return '/admin/storage/product/'


class ProductView(AdminInMixin, TemplateView):

    template_name = 'storage/product/view.html'

    def get_context_data(self, **kwargs):

        context = super(ProductView, self).get_context_data(**kwargs)
        product = Product.objects.get(id=self.kwargs['pk'])

        context['product'] = product
        context['product_group'] = product.product_kind.product_category.product_group.group_name
        context['product_category'] = product.product_kind.product_category.category_name
        context['product_kind'] = product.product_kind.kind_name
        context['form_type'] = 'view'

        return context


class ProductJsonView(ViewInMixin, FormView):

    def get(self, request, *args, **kwargs):

        json_data = {}
        export_type = request.GET['product_list']
        if export_type == 'all':
            json_data = get_products_all_json()
        elif export_type == 'balance':
            json_data = get_products_balance_json()
        elif export_type == 'product_add':
            json_data = get_kinds_for_product_add_json()
        elif export_type == 'wholesale':
            json_data = get_kinds_for_export_json('wholesale')
        elif export_type == 'revise':
            json_data = get_kinds_for_export_json('revise')

        return HttpResponse(json_data, content_type='json')


class ProductKindBaseView(StorageLogViewMixin, AdminInMixin):

    model = ProductKind
    form_class = ProductKindForm
    template_name = 'storage/product_kind/edit.html'

    def get_form_mode(self):
        raise NotImplementedError()

    def get_success_message(self):
        raise NotImplementedError()

    def get_log_info(self):
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        context = super(ProductKindBaseView, self).get_context_data(**kwargs)
        context['form_type'] = self.get_form_mode()
        context['category_list'] = ProductCategory.objects.select_related('product_group').all().order_by('product_group__group_name', 'category_name')

        return context

    @transaction.atomic
    def form_valid(self, form):
        response = super(ProductKindBaseView, self).form_valid(form)

        product_kind = form.instance
        Product.objects.filter(product_kind=product_kind.id).update(is_enable=product_kind.is_enable)

        messages.success(self.request, self.get_success_message() % product_kind.kind_name)
        self.log_info(self.get_log_info() % (self.request.user, product_kind))
        return response


class ProductKindAddView(ProductKindBaseView, CreateView):

    def get_form_mode(self):
        return 'add'

    def get_success_message(self):
        return 'Вид товара %s успешно добавлен!'

    def get_log_info(self):
        return 'Пользователь %s, добавил вид товара - %s'

    def get_success_url(self):
        return reverse('product_kind_add')


class ProductKindUpdateView(ProductKindBaseView, UpdateView):

    def get_form_mode(self):
        return 'edit'

    def get_success_message(self):
        return 'Вид товара %s успешно обновлен!'

    def get_log_info(self):
        return 'Пользователь %s, обновил вид товара - %s'

    def get_context_data(self, **kwargs):
        context = super(ProductKindUpdateView, self).get_context_data(**kwargs)
        context['product_kind_id'] = self.kwargs.get('pk')
        return context

    def get_success_url(self):
        return reverse('product_kind_edit', kwargs={'pk': self.kwargs.get('pk')})


class InvoiceCreate(StorageLogViewMixin, AdminInMixin, CreateView):

    model = Invoice
    form_class = InvoiceAddForm
    template_name = 'storage/invoice/add.html'

    def get_context_data(self, **kwargs):

        data = super(InvoiceCreate, self).get_context_data(**kwargs)
        data['providers'] = ProductProvider.objects.all().order_by('provider_name')
        data['invoice_status'] = Invoice.INVOICE_STATUS

        return data

    @transaction.atomic
    def form_valid(self, form):

        if form.ajax_field_errors:
            return HttpResponse(build_json_from_dict(form.ajax_field_errors), content_type='json')

        invoice = form.save(commit=False)
        invoice.invoice_date = form.cleaned_data.get('invoice_date') or timezone.now()
        invoice.owner = self.request.user
        invoice.save()

        shipments = str(form.cleaned_data['shipments']).split(',')

        invoice.shipments.set(list(Shipment.objects.filter(pk__in=shipments)))
        invoice.save()

        if invoice.status == Invoice.INVOICE_STATUS[1][0]:
            product_updater = StorageProductUpdater(invoice.shipments.select_related().all())
            product_updater.update()
            messages.success(self.request, 'Товар из приемки успешно добавлен на склад!')
        else:
            messages.warning(self.request, 'Приемка зафиксирована, для добавления товаров на склад обновите статус приемки на принято!')

        data = {
            'success': True,
            'id': invoice.id
        }

        self.log_info('Пользователь %s, добавил приемку товара - %s' % (self.request.user, form.instance))
        return HttpResponse(build_json_from_dict(data), content_type='json')


class InvoiceBuyReport(StorageLogViewMixin, ViewInMixin, TemplateView):

    template_name = 'storage/invoice/invoice_report.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(InvoiceBuyReport, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InvoiceBuyReport, self).get_context_data(**kwargs)
        period = get_period(self.request.GET.get(PERIOD_KEY), self.request.GET.get('period_start'),
                            self.request.GET.get('period_end'))
        context['report'] = InvoiceReportProcessor(period[0], period[1]).process()
        self.log_info('Пользователь %s, запросил отчет по приемке товара с %s по %s' % (self.request.user, format_date(period[0]), format_date(period[1])))
        return context


class InvoiceUpdateView(AdminInMixin, UpdateView):

    model = Invoice
    form_class = InvoiceUpdateForm
    template_name = 'storage/invoice/view.html'

    def get_context_data(self, **kwargs):
        context = super(InvoiceUpdateView, self).get_context_data(**kwargs)
        context['invoice_status'] = Invoice.INVOICE_STATUS
        context['invoice_shipments'] = context['invoice'].shipments.select_related().all().order_by('id')

        return context

    @transaction.atomic
    def form_valid(self, form):
        response = super(InvoiceUpdateView, self).form_valid(form)
        if form.is_accept_invoice():
            product_updater = StorageProductUpdater(form.instance.shipments.all())
            product_updater.update()
            messages.success(self.request, 'Товар из приемки успешно добавлен на склад!')

        if form.is_changed_invoice_date():
            messages.success(self.request, 'Время приемки успешно обновлено!')

        return response

    def get_success_url(self):
        return '/admin/storage/invoice/'

    def get_queryset(self):
        return Invoice.objects.select_related('owner', 'product_provider').prefetch_related('shipments')


class InvoiceDeleteView(AdminInMixin, DeleteView):

    def get_success_url(self):
        return '/admin/storage/invoice/'

    @transaction.atomic()
    def delete(self, request, *args, **kwargs):
        invoice = Invoice.objects.get(id=kwargs.get('pk'))

        if invoice.status == Invoice.INVOICE_STATUS[0][0]:
            invoice.delete()
            messages.success(request, 'Приемка со статусом черновик успешно удалена!')
        else:
            messages.warning(request, 'Приемку в статусе принято нельзя откатить!')

        return HttpResponseRedirect(self.get_success_url())


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
    template_name = 'storage/invoice/import_invoice.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(ImportProductViewMixin, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        file_processor = ProductExcelProcessor(form.cleaned_data.get('file'))
        file_processor.process()
        errors = file_processor.get_errors()
        self.log_info('Пользователь %s, инициировал загрузку товара на склад!' % self.request.user)
        return render(self.request, 'storage/invoice/import_invoice_result.html', context={'errors': errors})


class ExportProductViewMixin(StorageLogViewMixin, AdminInMixin, FormView, ExcelFileMixin):

    template_name = 'storage/product/export.html'
    form_class = ExportProductForm

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('export_type'):
            export_type = self.request.GET.get('export_type')
            if export_type == 'all':
                if not request.user.is_superuser:
                    return HttpResponseForbidden()
                else:
                    export_processor = ExportProductProcessor(export_type=export_type)
                    book = export_processor.generate_storage_file()
                    self.log_info(
                        'Пользователь %s, запросил полную выгрузку остатков товара со склада!' % self.request.user)
                    return self.build_response('StorageProducts', book)
        return super(ExportProductViewMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ExportProductViewMixin, self).get_context_data(**kwargs)
        context['export_type'] = self.request.GET.get('export_type')
        return context

    def form_valid(self, form):
        kinds = form.cleaned_data.get('kinds').split(',')
        export_processor = ExportProductProcessor(kinds, self.request.GET.get('export_type'))
        book = export_processor.generate_storage_file()

        self.log_info('Пользователь %s, запросил выгрузку остатков товара со склада!' % self.request.user)
        return self.build_response(book)


class ReviseAddView(FormView):

    template_name = 'storage/revise/revise_add.html'
    form_class = UploadFileForm

    def form_valid(self, form):
        processor = ReviseProductExcelProcessor(self.request.user, form.cleaned_data.get('file'))
        processor.process()

        context = {}
        if processor.get_errors():
            context['errors'] = processor.get_errors()
        else:
            messages.warning(self.request, 'Внимание при подтверждении сверки количество товаров изменится согласно колонке \'на складе\'!')
            context['revise'] = processor.get_result()

        return render(self.request, 'storage/revise/revise_add_confirm.html', context=context)


class ReviseAcceptView(View):

    def post(self, request, *args, **kwargs):
        revise = Revise.objects.get(pk=kwargs['pk'])
        revise.accept_revise()

        messages.success(self.request, 'Сверка товара прошла успешно!')
        return HttpResponseRedirect('/admin/storage/revise/')


class ReviseDeleteView(DeleteView):

    def delete(self, request, *args, **kwargs):

        with transaction.atomic():
            ProductRevise.objects.filter(revise=kwargs['pk']).delete()
            Revise.objects.filter(pk=kwargs['pk']).delete()
        messages.success(self.request, 'Сверка товара отменена!')
        return HttpResponseRedirect('/admin/storage/revise/')


class ReviseChangeView(StorageLogViewMixin, TemplateView):

    template_name = 'storage/revise/revise_view.html'

    def get_context_data(self, **kwargs):
        context = super(ReviseChangeView, self).get_context_data(**kwargs)
        revise = Revise.objects.select_related('owner').get(pk=kwargs['pk'])
        revise.calculate_loss()
        context['revise'] = revise
        if revise.status == 'DRAFT':
            messages.warning(self.request, 'Внимание при подтверждении сверки количество товаров изменится согласно колонке \'на складе\'!')
        self.log_info('Пользователь %s, запросил просмотр сверки товара revise_id=%s!' % (self.request.user, kwargs['pk']))
        return context
