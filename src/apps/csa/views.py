from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from hookah_crm import settings
from src.apps.csa.forms import LoginForm
from src.apps.ext_user.user_helper import is_employer


# Действия при авторизации
from src.apps.ext_user.user_service import create_open_work_session, close_open_work_session


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
                start_employer_session(user)
                return redirect(to='/admin/')
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

    return redirect(to=settings.LOGIN_URL)


# Заканчиваем сессию работника
def end_employer_session(user):

    if is_employer(user):
        close_open_work_session(user)

