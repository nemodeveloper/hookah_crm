# Generated by Django 2.2.10 on 2020-02-10 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0003_auto_20200202_0236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price_discount',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Опт 5к'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_shop',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Опт 20к'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_wholesale',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Опт 100к'),
        ),
    ]
