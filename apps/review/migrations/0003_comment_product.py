import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0002_wipe_comments"),
        ("product", "0026_wipe_catalog"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="comment", name="unique_variant_user_comment"
        ),
        migrations.RemoveField(model_name="comment", name="variant"),
        migrations.AddField(
            model_name="comment",
            name="product",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="product.product",
            ),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name="comment",
            constraint=models.UniqueConstraint(
                fields=("product", "user"), name="unique_product_user_comment"
            ),
        ),
    ]
