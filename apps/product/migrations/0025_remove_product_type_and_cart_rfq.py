from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0024_remove_both_product_type"),
        ("order", "0012_remove_rfq"),
    ]

    operations = [
        migrations.RemoveField(model_name="cartitem", name="attributes"),
        migrations.RemoveField(model_name="cartitem", name="deadline"),
        migrations.RemoveField(model_name="product", name="product_type"),
        migrations.RemoveField(model_name="productconstructor", name="product_type"),
    ]
