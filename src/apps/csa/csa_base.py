from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.utils.decorators import method_decorator


from django.views.decorators.csrf import csrf_exempt
from openpyxl.writer.excel import save_virtual_workbook

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


class ExcelFileMixin(object):

    excel_file_name = None

    def get_excel_file_name(self):
        return self.excel_file_name

    def build_response(self, book, file_name=None):
        file_name = file_name if file_name \
            else self.excel_file_name if self.excel_file_name \
            else self.get_excel_file_name()

        if file_name is None:
            file_name = 'UnknownExcelFile'

        response = HttpResponse(save_virtual_workbook(book),
                                content_type='application/vnd.ms-excel; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=%s.xlsx' % file_name
        return response
