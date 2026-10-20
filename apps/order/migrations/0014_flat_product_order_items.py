import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0013_wipe_orders"),
        ("product", "0026_wipe_catalog"),
    ]

    operations = [
        migrations.RemoveField(model_name="orderitem", name="product_variant"),
        migrations.RemoveField(model_name="orderitem", name="attribute_stock"),
        migrations.RemoveField(model_name="orderitem", name="category"),
        migrations.RemoveField(model_name="orderitem", name="description"),
        migrations.RemoveField(model_name="orderitem", name="price_min"),
        migrations.RemoveField(model_name="orderitem", name="price_max"),
        migrations.RemoveField(model_name="order", name="company"),
        migrations.AddField(
            model_name="orderitem",
            name="product",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_items",
                to="product.product",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="orderitem",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14),
        ),
    ]
