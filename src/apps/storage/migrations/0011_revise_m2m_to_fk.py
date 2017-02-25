# -*- coding: utf-8 -*-
from django.db import migrations

from src.apps.storage.models import Revise, ProductRevise


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0010_auto_20170225_2056'),
    ]

    def migrate_revise_m2m_to_fk(apps, schema_editor):

        # перекидываем связи
        for revise in Revise.objects.prefetch_related('products_revise').all():
            for product_revise in revise.products_revise.all():
                product_revise.revise = revise
                product_revise.save()

        # удаляем мусор
        for product_revise in ProductRevise.objects.all():
            if not product_revise.revise_id:
                product_revise.delete()

    operations = [
        migrations.RunPython(migrate_revise_m2m_to_fk)
    ]
