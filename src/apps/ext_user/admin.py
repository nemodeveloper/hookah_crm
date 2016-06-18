from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from src.apps.ext_user.forms import UserChangeForm, UserCreationForm
from src.apps.ext_user.models import ExtUser, WorkSession, WorkProfile


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
        ('Статус пользователя', {'fields': ('is_superuser', 'is_admin',)}),
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


@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):

    list_display = ('ext_user', 'start_workday', 'end_workday',)
    ordering = ('start_workday',)
    date_hierarchy = 'start_workday'
    search_fields = ('ext_user__last_name', 'ext_user__first_name')


@admin.register(WorkProfile)
class WorkProfileAdmin(admin.ModelAdmin):

    list_display = ('ext_user', 'money_per_hour', 'percent_per_sale',)
    ordering = ('ext_user',)
    search_fields = ('ext_user__last_name', 'ext_user__first_name')


