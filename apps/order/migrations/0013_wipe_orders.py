from django.db import migrations


def wipe_orders(apps, schema_editor):
    # Order items used to point at variants; the catalog is rebuilt on the flat
    # product model, so the old demo orders can't be carried over.
    apps.get_model("order", "OrderItem").objects.all().delete()
    apps.get_model("order", "Order").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0012_remove_rfq"),
    ]

    operations = [
        migrations.RunPython(wipe_orders, migrations.RunPython.noop),
    ]
