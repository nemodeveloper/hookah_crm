# Generated by Django 3.0.2 on 2020-02-03 01:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_initial_create'),
        ('cashbox', '0002_auto_20200202_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsell',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='market.Customer', verbose_name='Покупатель'),
        ),
    ]
