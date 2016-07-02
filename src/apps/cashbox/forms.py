from django import forms
from django.core.validators import MinValueValidator

from src.apps.cashbox.models import CashTake, PaymentType, ProductSell, ProductShipment
from src.form_components.form_processor import FormData, FormProcessor


class CashTakeAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CashTakeAdminForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea(attrs={'cols': 60, 'rows': 5})

    class Meta:
        fields = '__all__'
        model = CashTake


class ProductSellForm(forms.ModelForm):

    shipments = forms.CharField()
    payments = forms.CharField()

    def clean_shipments(self):

        # TODO поправить на клиенте
        temp = self.cleaned_data.get('shipments')
        return temp[:-1]

    def clean_payments(self):

        temp = self.cleaned_data.get('payments')
        return temp[:-1]

    class Meta:

        model = ProductSell
        exclude = ['sell_date', 'seller']


class ProductShipmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.ajax_field_errors = {}
        super(ProductShipmentForm, self).__init__(*args, **kwargs)

    def clean(self):

        cost_price = self.cleaned_data.get('cost_price')
        cost_price_data = FormData('cost_price', cost_price,
                                   forms.DecimalField(required=True, max_digits=8, decimal_places=2, validators=[
                                       MinValueValidator(limit_value=0.01, message='Поле стоимость продажи должно быть больше 0!')
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
        model = ProductShipment


class PaymentTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.ajax_field_errors = {}
        super(PaymentTypeForm, self).__init__(*args, **kwargs)

    def clean(self):

        cash = self.cleaned_data.get('cash')
        cash_data = FormData('cash', cash,
                             forms.DecimalField(required=True, max_digits=8, decimal_places=2, validators=[
                                 MinValueValidator(limit_value=0.01, message='Поле Сумма должно быть больше 0!')
                             ]))

        form_processor = FormProcessor([cash_data])
        self.ajax_field_errors = form_processor.process()

        return self.cleaned_data

    class Meta:

        fields = '__all__'
        model = PaymentType

