from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0014_flat_product_order_items"),
    ]

    operations = [
        migrations.RemoveField(model_name="order", name="status"),
        migrations.RemoveField(model_name="order", name="is_closed"),
        migrations.RemoveField(model_name="order", name="discount"),
        migrations.RemoveField(model_name="order", name="discount_budget"),
        migrations.RemoveField(model_name="order", name="accepted_by_buyer"),
        migrations.RemoveField(model_name="order", name="accepted_by_seller"),
        migrations.RemoveField(model_name="order", name="rejected_by_buyer"),
        migrations.RemoveField(model_name="order", name="rejected_by_seller"),
    ]
