from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator


from django.views.decorators.csrf import csrf_exempt

from src.template_tags.common_tags import check_perm


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


class CheckPermInMixin(AdminInMixin):

    def get_perm_key(self):
        raise NotImplementedError()

    def dispatch(self, request, *args, **kwargs):
        if check_perm(request.user, self.get_perm_key()):
            return super(CheckPermInMixin, self).dispatch(request, *args, **kwargs)
        return HttpResponseForbidden()
