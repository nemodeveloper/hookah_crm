# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-26 20:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0004_auto_20161025_2340'),
    ]

    operations = [
        migrations.AddField(
            model_name='productkind',
            name='min_count',
            field=models.IntegerField(default=10, verbose_name='Минимальное количество'),
        ),
    ]
