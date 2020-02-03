from django import forms

from src.apps.market.models import Customer


class CustomerAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CustomerAdminForm, self).__init__(*args, **kwargs)

        self.fields['main_contact'].widget = forms.Textarea(attrs={'cols': 32, 'rows': 4})
        self.fields['phone_number'].widget = forms.Textarea(attrs={'cols': 32, 'rows': 4})
        self.fields['communication_links'].widget = forms.Textarea(attrs={'cols': 128, 'rows': 4})
        self.fields['address'].widget = forms.Textarea(attrs={'cols': 64, 'rows': 4})
        self.fields['description'].widget = forms.Textarea(attrs={'cols': 128, 'rows': 4})

    class Meta:
        fields = '__all__'
        model = Customer
