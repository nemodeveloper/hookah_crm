# Generated by Django 2.2.10 on 2020-05-07 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0010_auto_20200507_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Дисконт'),
        ),
    ]