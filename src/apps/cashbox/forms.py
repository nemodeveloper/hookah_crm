from django import forms
from django.core.validators import MinValueValidator

from hookah_crm import settings
from src.apps.cashbox.models import PaymentType, ProductSell, ProductShipment
from src.base_components.form_components.form_processor import FormData, FormProcessor


class ProductSellForm(forms.ModelForm):

    shipments = forms.CharField()
    payments = forms.CharField()
    customer_id = forms.CharField()
    sell_date = forms.DateTimeField(required=False, input_formats=[settings.CLIENT_DATE_FORMAT])

    class Meta:
        model = ProductSell
        exclude = ['seller', 'customer', ]


class ProductSellUpdateForm(forms.ModelForm):

    sell_date = forms.DateTimeField(required=True, input_formats=[settings.CLIENT_DATE_FORMAT])

    class Meta:

        model = ProductSell
        fields = ['sell_date', ]


class ProductShipmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProductShipmentForm, self).__init__(*args, **kwargs)
        self.ajax_field_errors = {}

    def clean(self):

        # TODO как будет время перейти на стандартную валидацию
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
        exclude = ['initial_cost_price', 'product_cost_price', 'sell', ]
        model = ProductShipment


class PaymentTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PaymentTypeForm, self).__init__(*args, **kwargs)
        self.ajax_field_errors = {}

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
        exclude = ['sell', ]
        model = PaymentType
