# Generated by Django 2.2.10 on 2020-05-07 22:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0009_remove_product_product_image'),
    ]

    operations = [
        migrations.RenameField(model_name='Product', old_name='price_discount', new_name='price_opt_1'),
        migrations.RenameField(model_name='Product', old_name='price_shop', new_name='price_opt_2'),
        migrations.RenameField(model_name='Product', old_name='price_wholesale', new_name='price_opt_3')
    ]