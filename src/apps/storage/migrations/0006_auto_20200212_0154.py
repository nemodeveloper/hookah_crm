# Generated by Django 2.2.10 on 2020-02-12 01:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0005_shipment_invoice'),
    ]

    operations = [
        migrations.RunSQL("UPDATE storage_shipment "
                          "SET invoice_id = mm.invoice_id "
                          "FROM storage_invoice_shipments mm "
                          "WHERE storage_shipment.id = mm.shipment_id"),
        migrations.RunSQL("DELETE FROM storage_shipment WHERE invoice_id IS NULL"),
    ]