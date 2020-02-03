from django.db import migrations


RETAIL_CUSTOMER = u'Розница'


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    CustomerType = apps.get_model("market", "CustomerType")
    Customer = apps.get_model("market", "Customer")

    db_alias = schema_editor.connection.alias
    CustomerType.objects.using(db_alias).bulk_create([
        CustomerType(type_name=RETAIL_CUSTOMER),
    ])
    Customer.objects.using(db_alias).bulk_create([
        Customer(name=RETAIL_CUSTOMER, customer_type=CustomerType.objects.using(db_alias)
                 .filter(type_name=RETAIL_CUSTOMER).first())
    ])


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [('market', '0001_initial'), ]
    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
