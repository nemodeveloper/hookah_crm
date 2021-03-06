# Generated by Django 2.2.10 on 2020-02-12 02:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cashbox', '0013_auto_20200211_0031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenttype',
            name='sell',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='cashbox.ProductSell', verbose_name='Продажа'),
        ),
        migrations.AlterField(
            model_name='productshipment',
            name='sell',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipments', to='cashbox.ProductSell', verbose_name='Продажа'),
        ),
    ]
