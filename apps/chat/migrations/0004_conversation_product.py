import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0003_alter_conversation_buyer_alter_conversation_seller_and_more"),
        ("product", "0026_wipe_catalog"),
    ]

    operations = [
        migrations.RemoveField(model_name="conversation", name="product_variant"),
        migrations.AddField(
            model_name="conversation",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="conversations",
                to="product.product",
            ),
        ),
    ]
