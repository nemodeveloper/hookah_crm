# Generated by Django 2.2.10 on 2020-02-11 00:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cashbox', '0009_auto_20200211_0015'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenttype',
            name='sell',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='has_payments', to='cashbox.ProductSell', verbose_name='Продажа'),
        ),
    ]
