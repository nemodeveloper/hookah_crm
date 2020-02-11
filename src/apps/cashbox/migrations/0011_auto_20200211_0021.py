# Generated by Django 2.2.10 on 2020-02-11 00:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cashbox', '0010_paymenttype_sell'),
    ]

    operations = [
        migrations.RunSQL("UPDATE cashbox_payment_type "
                          "SET sell_id = mm.productsell_id "
                          "FROM cashbox_product_sell_payments mm "
                          "WHERE cashbox_payment_type.id = mm.paymenttype_id"),
        migrations.RunSQL("DELETE FROM cashbox_payment_type WHERE sell_id IS NULL"),
    ]