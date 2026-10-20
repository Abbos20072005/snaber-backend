from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0027_flat_product"),
    ]

    operations = [
        migrations.RemoveField(model_name="product", name="view_count"),
    ]
