from django import forms

from src.apps.cashbox.models import CashTake, PaymentType


class CashTakeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CashTakeForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea(attrs={'cols': 60, 'rows': 5})

    class Meta:
        fields = '__all__'
        model = CashTake


class PaymentTypeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PaymentTypeForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea(attrs={'cols': 60, 'rows': 5})

    class Meta:
        fields = '__all__'
        model = PaymentType
