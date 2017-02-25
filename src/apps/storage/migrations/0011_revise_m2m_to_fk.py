# -*- coding: utf-8 -*-
from django.db import migrations

from src.apps.storage.models import Revise, ProductRevise


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0010_auto_20170225_2056'),
    ]

    # перекидываем связи
    def migrate_revise_m2m_to_fk(apps, schema_editor):
        for revise in Revise.objects.prefetch_related('products_revise').all():
            for product_revise in revise.products_revise.all():
                product_revise.revise = revise
                product_revise.save()

    # удаляем мусор
    def delete_revise_trash(apps, schema_editor):
        ProductRevise.objects.filter(revise__isnull=True).delete()

    operations = [
        migrations.RunPython(migrate_revise_m2m_to_fk),
        migrations.RunPython(delete_revise_trash)
    ]
