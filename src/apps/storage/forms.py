from django import forms
from django.core.validators import MinValueValidator

from hookah_crm import settings
from src.apps.storage.models import ProductProvider, Invoice, Shipment, Product, ProductKind
from src.base_components.form_components.form_processor import FormData, FormProcessor


class ProductProviderAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProductProviderAdminForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea(attrs={'cols': 60, 'rows': 5})

    class Meta:
        fields = '__all__'
        model = ProductProvider


class ProductForm(forms.ModelForm):

    update_kind = forms.BooleanField(required=False)

    class Meta:

        model = Product
        exclude = ['change_date']


class ProductKindForm(forms.ModelForm):

    class Meta:
        fields = '__all__'
        model = ProductKind


class InvoiceAddForm(forms.ModelForm):

    shipments = forms.CharField(required=True)
    invoice_date = forms.DateTimeField(required=False, input_formats=[settings.CLIENT_DATE_FORMAT])

    def __init__(self, *args, **kwargs):
        self.ajax_field_errors = {}
        super(InvoiceAddForm, self).__init__(*args, **kwargs)

    def clean(self):

        shipments = self.cleaned_data.get('shipments')
        shipments_data = FormData('shipments', shipments, forms.CharField(required=True))

        overhead = self.cleaned_data.get('overhead')
        overhead_data = FormData('overhead', overhead,
                                 forms.DecimalField(required=True, max_digits=8, decimal_places=2, validators=[
                                     MinValueValidator(limit_value=-0.01, message='Поле издержки должно быть больше или равно 0!')
                                 ]))

        form_processor = FormProcessor([overhead_data, shipments_data])
        self.ajax_field_errors = form_processor.process()

        return self.cleaned_data

    class Meta:

        model = Invoice
        exclude = ['owner']


class InvoiceUpdateForm(forms.ModelForm):

    invoice_date = forms.DateTimeField(required=False, input_formats=[settings.CLIENT_DATE_FORMAT])
    status = forms.CharField(required=False)

    def clean_invoice_date(self):
        if self.cleaned_data['invoice_date']:
            return self.cleaned_data['invoice_date']
        return self.initial['invoice_date']

    def clean_status(self):
        if self.cleaned_data['status']:
            return self.cleaned_data['status']
        return self.initial['status']

    def is_accept_invoice(self):
        return 'status' in self.changed_data \
            and self.initial.get('status') == Invoice.INVOICE_STATUS[0][0]\
            and self.instance.status == Invoice.INVOICE_STATUS[1][0]

    def is_changed_invoice_date(self):
        return 'invoice_date' in self.changed_data and self.initial.get('invoice_date') != self.instance.invoice_date

    class Meta:
        model = Invoice
        fields = ['invoice_date', 'status', 'overhead']


class ShipmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ShipmentForm, self).__init__(*args, **kwargs)
        self.ajax_field_errors = {}

    def clean(self):

        cost_price = self.cleaned_data.get('cost_price')
        cost_price_data = FormData('cost_price', cost_price,
                                   forms.DecimalField(required=True, max_digits=8, decimal_places=2, validators=[
                                       MinValueValidator(limit_value=0.01, message='Поле стоимость должно быть больше 0!')
                                   ]))

        product_count = self.cleaned_data.get('product_count')
        product_count_data = FormData('product_count', product_count,
                                      forms.IntegerField(required=True, validators=[
                                          MinValueValidator(limit_value=1, message='Поле количество должно быть больше 1!')
                                      ]))

        form_processor = FormProcessor([cost_price_data, product_count_data])
        self.ajax_field_errors = form_processor.process()

        return self.cleaned_data

    class Meta:
        exclude = ['invoice']
        model = Shipment


class ExportProductForm(forms.Form):

    kinds = forms.CharField(required=True)
