from django.db import migrations, models

CHOICES = [("ready", "Ready"), ("made_to_order", "Made to order")]


def both_to_ready(apps, schema_editor):
    for name in ("Product", "ProductConstructor"):
        apps.get_model("product", name).objects.filter(product_type="both").update(
            product_type="ready"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0023_product_creator_productconstructor_creator"),
    ]

    operations = [
        migrations.RunPython(both_to_ready, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="product",
            name="product_type",
            field=models.CharField(choices=CHOICES, default="ready", max_length=20),
        ),
        migrations.AlterField(
            model_name="productconstructor",
            name="product_type",
            field=models.CharField(choices=CHOICES, default="ready", max_length=20),
        ),
    ]
