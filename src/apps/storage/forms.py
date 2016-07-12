from django import forms
from django.core.validators import MinValueValidator

from src.apps.storage.models import ProductProvider, Invoice, Shipment, Product, ProductStorage
from src.form_components.form_processor import FormData, FormProcessor


class ProductProviderAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProductProviderAdminForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea(attrs={'cols': 60, 'rows': 5})

    class Meta:
        fields = '__all__'
        model = ProductProvider


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product
        exclude = ['product_image']


class ProductStorageForm(forms.ModelForm):

    class Meta:

        model = ProductStorage
        fields = '__all__'


class InvoiceAddForm(forms.ModelForm):

    shipments = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.ajax_field_errors = {}
        super(InvoiceAddForm, self).__init__(*args, **kwargs)

    def clean(self):

        shipments = self.cleaned_data.get('shipments')
        shipments_data = FormData('shipments', shipments, forms.CharField(required=True))

        overhead = self.cleaned_data.get('overhead')
        overhead_data = FormData('overhead', overhead,
                                 forms.DecimalField(required=True, max_digits=8, decimal_places=2, validators=[
                                     MinValueValidator(limit_value=0.01, message='Поле издержки должно быть больше 0!')
                                 ]))

        form_processor = FormProcessor([overhead_data, shipments_data])
        self.ajax_field_errors = form_processor.process()

        return self.cleaned_data

    class Meta:

        model = Invoice
        exclude = ['invoice_date', 'owner']


class InvoiceViewForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = '__all__'


class ShipmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.ajax_field_errors = {}
        super(ShipmentForm, self).__init__(*args, **kwargs)

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

        fields = '__all__'
        model = Shipment
