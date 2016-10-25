from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Базовый класс для доступа авторизованных клиентов
from django.views.decorators.csrf import csrf_exempt


class LoggedInMixin(object):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(request, *args, **kwargs)


# Базовый класс для доступа к функционалу административной части
class AdminInMixin(LoggedInMixin):

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminInMixin, self).dispatch(request, *args, **kwargs)


# Базовый класс для просмотра сущностей системы, без csrf - токена
class ViewInMixin(LoggedInMixin):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ViewInMixin, self).dispatch(request, *args, **kwargs)
