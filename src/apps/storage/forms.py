from django import forms

from src.apps.storage.models import ProductProvider


class ProductProviderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProductProviderForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea(attrs={'cols': 60, 'rows': 5})

    class Meta:
        fields = '__all__'
        model = ProductProvider
