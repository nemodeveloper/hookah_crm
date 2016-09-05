from datetime import timedelta
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect

from src.apps.ext_user.forms import UserChangeForm, UserCreationForm
from src.apps.ext_user.models import ExtUser, WorkSession, WorkProfile
from src.common_helper import date_to_verbose_format


@admin.register(ExtUser)
class UserAdmin(UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {
         'fields': (
             'last_name',
             'first_name',
             'father_name',
         )}),
        ('Статус пользователя', {'fields': ('is_superuser', 'is_admin', 'is_active')}),
        ('Права доступа', {'fields': ('groups',)}),
        ('Важные события', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
            )}
         ),
    )

    list_display = ['email', 'last_name', 'first_name', 'is_active', 'is_admin']
    list_filter = ['is_admin']
    search_fields = ('last_name', 'first_name', 'email',)
    ordering = ('last_name', 'first_name',)
    filter_horizontal = ('groups',)

    def view_employer_work_day_report(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if len(selected) > 1 or not selected:
            self.message_user(request, "Для формирования отчета необходимо выбрать 1 сотрудника!")
        else:
            return HttpResponseRedirect("/admin/cashbox/productsell/report/employer/%s/" % selected[0])
    view_employer_work_day_report.short_description = "Отчет по работнику"

    actions = [view_employer_work_day_report]


@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {'fields': ['ext_user', 'session_status', 'start_workday', 'end_workday']}),
    )
    list_display = ('ext_user', 'session_status', 'get_verbose_start_workday', 'get_verbose_end_workday', 'get_work_time')
    ordering = ('-start_workday',)
    date_hierarchy = 'start_workday'
    search_fields = ('ext_user__last_name', 'ext_user__first_name')

    def get_work_time(self, obj):
        if obj.session_status == 'CLOSE':
            time_difference = obj.end_workday - obj.start_workday
            minutes = time_difference / timedelta(minutes=1)
            hours_minutes = divmod(minutes, 60)
            if hours_minutes[1] > 45:
                return hours_minutes[0] + 1
            return hours_minutes[0]
        return '-'
    get_work_time.short_description = 'Отработано'

    def get_verbose_start_workday(self, obj):
        return date_to_verbose_format(obj.start_workday)
    get_verbose_start_workday.short_description = 'Начало рабочего дня'

    def get_verbose_end_workday(self, obj):
        return date_to_verbose_format(obj.end_workday)
    get_verbose_end_workday.short_description = 'Конец рабочего дня'


@admin.register(WorkProfile)
class WorkProfileAdmin(admin.ModelAdmin):

    list_display = ('ext_user', 'money_per_hour', 'percent_per_sale',)
    ordering = ('ext_user',)
    search_fields = ('ext_user__last_name', 'ext_user__first_name')


