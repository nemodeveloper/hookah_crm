from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render

from hookah_crm import settings
from src.apps.csa.forms import LoginForm
from src.apps.ext_user.service import is_employer

from src.apps.ext_user.service import create_open_work_session, close_open_work_session


# Действия при авторизации
def login_view(request):

    if request.method != 'POST':
        form = LoginForm()
        return render(request,
                      template_name='auth/login.html',
                      context={'form': form})

    form = LoginForm(request.POST)
    if form.is_valid():
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])

        if user is not None:
            if user.is_active:

                login(request, user)
                end_employer_session(user)
                start_employer_session(user)
                return HttpResponseRedirect(redirect_to='/admin/')
            else:
                form.add_error(field='', error='Ваш аккаунт заблокирован!')

        else:
            form.add_error(field='', error='Вы указали неверный логин или пароль!')

    return render(request,
                  template_name='auth/login.html',
                  context={'form': form})


# Начинаем сессию работника
def start_employer_session(user):
    if is_employer(user):
        create_open_work_session(user)


# Действия при выходе
def logout_view(request):
    end_employer_session(request.user)
    logout(request)
    clear_cookies(request)
    return HttpResponseRedirect(redirect_to=settings.LOGIN_URL)


def clear_cookies(request):
    request.COOKIES.clear()


# Заканчиваем сессию работника
def end_employer_session(user):
    if is_employer(user):
        close_open_work_session(user)

