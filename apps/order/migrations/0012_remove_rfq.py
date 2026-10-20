from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0011_remove_both_order_type"),
    ]

    operations = [
        migrations.DeleteModel(name="RFQOrderItemAttribute"),
        migrations.RemoveField(model_name="order", name="deadline"),
        migrations.RemoveField(model_name="order", name="order_type"),
    ]
