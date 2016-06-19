from django import forms


class LoginForm(forms.Form):

    username = forms.CharField(label='Электронная почта(Логин)', max_length=255)
    password = forms.CharField(label='Пароль', max_length=128, widget=forms.PasswordInput)

    def clean(self):

        if (not self.cleaned_data.get('username')) or (not self.cleaned_data.get('password')):
            raise forms.ValidationError('Вы указали неверный логин или пароль!',
                                        code='invalid',
                                        params={'password': ''})
        return self.cleaned_data
