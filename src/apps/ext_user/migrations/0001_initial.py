# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-12 20:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(db_index=True, max_length=255, unique=True, verbose_name='Электронная почта')),
                ('last_name', models.CharField(max_length=40, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=40, verbose_name='Имя')),
                ('father_name', models.CharField(max_length=40, verbose_name='Отчество')),
                ('register_date', models.DateField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('is_admin', models.BooleanField(default=False, verbose_name='Администратор')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'db_table': 'ext_user_user',
            },
        ),
        migrations.CreateModel(
            name='WorkProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money_per_hour', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Оплата за час работы')),
                ('percent_per_sale', models.IntegerField(verbose_name='Процент от продажи')),
                ('ext_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_work_profiles', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Профиль продавца',
                'verbose_name_plural': 'Профили продавцов',
                'db_table': 'ext_user_work_profile',
            },
        ),
        migrations.CreateModel(
            name='WorkSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_workday', models.DateTimeField(verbose_name='Начало рабочего дня')),
                ('end_workday', models.DateTimeField(blank=True, verbose_name='Конец рабочего дня')),
                ('ext_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_work_sessions', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'ordering': ['start_workday'],
                'verbose_name': 'Сессия работника',
                'verbose_name_plural': 'Сессии работников',
                'db_table': 'ext_user_work_session',
            },
        ),
    ]
