from datetime import timedelta, datetime

from django.contrib.auth.models import PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.db import models

from hookah_crm import settings


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Некоректное поле Email')

        user = self.model(email=UserManager.normalize_email(email),)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class ExtUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(u'Электронная почта', max_length=255, unique=True, db_index=True)
    last_name = models.CharField(u'Фамилия', max_length=40)
    first_name = models.CharField(u'Имя', max_length=40)
    father_name = models.CharField('Отчество', max_length=40)
    register_date = models.DateField(u'Дата регистрации', auto_now_add=True)
    is_active = models.BooleanField(u'Активен', default=True)
    is_admin = models.BooleanField(u'Администратор', default=False)

    def get_full_name(self):
        if self.last_name and self.first_name and self.father_name:
            return '%s %s %s' % (self.last_name, self.first_name, self.father_name)
        return self.get_short_name()

    @property
    def is_staff(self):
        return self.is_admin

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.get_full_name()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = u'Пользователь'
        verbose_name_plural = u'Пользователи'
        db_table = 'ext_user_user'


class WorkSession(models.Model):

    WorkSessionStatus = (
        ('OPEN', 'Открыта'),
        ('CLOSE', 'Закрыта'),
        ('OVER', 'Просрочена'),
        ('UNKNOW', 'Неизвестно'),
    )

    ext_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name=u'Пользователь', related_name='user_work_sessions', on_delete=models.PROTECT)
    session_status = models.CharField('Статус', choices=WorkSessionStatus, max_length=10, default='UNKNOW')
    start_workday = models.DateTimeField(u'Начало рабочего дня')
    end_workday = models.DateTimeField(u'Конец рабочего дня', null=True)

    def get_work_hours(self):
        if self.session_status in ('CLOSE', 'OVER'):
            time_difference = self.end_workday - self.start_workday
            minutes = time_difference / timedelta(minutes=1)
            hours_minutes = divmod(minutes, 60)
            if hours_minutes[1] > 45:
                return hours_minutes[0] + 1
            return hours_minutes[0]
        return 0

    def close_session(self):
        if self.session_status != 'OPEN':
            return

        cur_datetime = datetime.now()
        cur_date = cur_datetime.date()

        start_session_date = self.start_workday.date()

        if cur_date.day == start_session_date.day:
            if cur_datetime.hour == 23 and cur_datetime.minute > 40:
                self.session_status = 'OVER'
            else:
                self.session_status = 'CLOSE'
        else:
            self.session_status = 'OVER'

        self.end_workday = cur_datetime
        self.save()

    def __str__(self):
        if self.end_workday:
            end_day = self.end_workday.strftime('%Y-%m-%d %H:%M')
        else:
            end_day = ""
        return '%s - %s - %s' % (str(self.ext_user),
                                 self.start_workday.strftime('%Y-%m-%d %H:%M'),
                                 end_day)

    class Meta:
        ordering = ['start_workday']
        verbose_name = 'Сессия работника'
        verbose_name_plural = 'Сессии работников'
        db_table = 'ext_user_work_session'


class WorkProfile(models.Model):

    ext_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name=u'Пользователь',
                                 related_name='user_work_profiles', on_delete=models.PROTECT)
    money_per_hour = models.DecimalField(u'Оплата за час работы', max_digits=5, decimal_places=2)
    percent_per_sale = models.IntegerField(u'Процент от продажи')

    def __str__(self):
        return str(self.ext_user)

    class Meta:
        verbose_name = 'Профиль продавца'
        verbose_name_plural = 'Профили продавцов'
        db_table = 'ext_user_work_profile'

