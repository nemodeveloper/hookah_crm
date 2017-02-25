# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 00:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0012_remove_revise_products_revise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productrevise',
            name='revise',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products_revise', to='storage.Revise', verbose_name='Сверка'),
        ),
    ]
