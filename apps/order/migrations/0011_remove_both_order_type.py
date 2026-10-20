from django.db import migrations, models


def both_to_ready(apps, schema_editor):
    apps.get_model("order", "Order").objects.filter(order_type="both").update(
        order_type="ready"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0010_alter_order_company"),
    ]

    operations = [
        migrations.RunPython(both_to_ready, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="order",
            name="order_type",
            field=models.CharField(
                choices=[("ready", "Ready"), ("rfq", "RFQ")],
                default="ready",
                max_length=10,
            ),
        ),
    ]
