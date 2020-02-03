from django.db import migrations


RETAIL_CUSTOMER = u'Розница'


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    ProductSell = apps.get_model("cashbox", "ProductSell")
    Customer = apps.get_model("market", "Customer")

    db_alias = schema_editor.connection.alias
    ProductSell.objects.using(db_alias).all()\
        .update(customer=Customer.objects.using(db_alias).filter(name=RETAIL_CUSTOMER).first())


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [('cashbox', '0003_productsell_customer'), ]
    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
