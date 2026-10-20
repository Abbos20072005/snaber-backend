import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0026_wipe_catalog"),
        ("order", "0014_flat_product_order_items"),
        ("review", "0003_comment_product"),
        ("chat", "0004_conversation_product"),
    ]

    operations = [
        # Moderation constructors and variants are gone: a product is one flat row.
        migrations.DeleteModel(name="VariantAttributeStockConstructor"),
        migrations.DeleteModel(name="VariantMediaConstructor"),
        migrations.DeleteModel(name="ProductAttributeValueConstructor"),
        migrations.DeleteModel(name="CharacteristicConstructor"),
        migrations.DeleteModel(name="VariantConstructor"),
        migrations.DeleteModel(name="ProductConstructor"),
        migrations.RemoveField(model_name="cartitem", name="attribute_stock"),
        migrations.RemoveField(model_name="cartitem", name="company"),
        migrations.DeleteModel(name="VariantAttributeStock"),
        migrations.DeleteModel(name="VariantMedia"),
        migrations.DeleteModel(name="Characteristic"),
        migrations.AlterUniqueTogether(name="productattributevalue", unique_together=set()),
        migrations.RemoveField(model_name="productattributevalue", name="product"),
        migrations.RemoveField(model_name="cartitem", name="product"),
        migrations.DeleteModel(name="Variant"),
        migrations.AddField(
            model_name="cartitem",
            name="product",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cart_items",
                to="product.product",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="productattributevalue",
            name="product",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_attribute_values",
                to="product.product",
            ),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="productattributevalue",
            unique_together={("product", "attribute", "attribute_value")},
        ),
        # Product
        migrations.RemoveField(model_name="product", name="owner"),
        migrations.RemoveField(model_name="product", name="creator"),
        migrations.RemoveField(model_name="product", name="image"),
        migrations.RemoveField(model_name="product", name="price_type"),
        migrations.RemoveField(model_name="product", name="price_min"),
        migrations.RemoveField(model_name="product", name="price_max"),
        migrations.RemoveField(model_name="product", name="moq"),
        migrations.RemoveField(model_name="product", name="moq_unit"),
        migrations.RemoveField(model_name="product", name="lead_time_min"),
        migrations.RemoveField(model_name="product", name="lead_time_max"),
        migrations.AlterModelOptions(
            name="product",
            options={
                "ordering": ("-created_at",),
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
            },
        ),
        migrations.AlterField(
            model_name="product",
            name="sku",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="category_products",
                to="product.category",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="product",
            name="description_en",
            field=models.TextField(blank=True, default="", null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="description_ru",
            field=models.TextField(blank=True, default="", null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="description_uz",
            field=models.TextField(blank=True, default="", null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="unit",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="unit_products",
                to="product.unit",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14),
        ),
        migrations.AddField(
            model_name="product",
            name="discount_percent",
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[django.core.validators.MaxValueValidator(100)],
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="stock_quantity",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("file", models.FileField(upload_to="products/files/")),
                ("position", models.PositiveSmallIntegerField(default=0)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="product.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product image",
                "verbose_name_plural": "Product images",
                "ordering": ("position", "id"),
            },
        ),
        migrations.CreateModel(
            name="ProductCharacteristic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("name", models.CharField(max_length=255)),
                ("name_en", models.CharField(max_length=255, null=True)),
                ("name_ru", models.CharField(max_length=255, null=True)),
                ("name_uz", models.CharField(max_length=255, null=True)),
                ("value", models.CharField(max_length=255)),
                ("value_en", models.CharField(max_length=255, null=True)),
                ("value_ru", models.CharField(max_length=255, null=True)),
                ("value_uz", models.CharField(max_length=255, null=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="characteristics",
                        to="product.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product characteristic",
                "verbose_name_plural": "Product characteristics",
                "ordering": ("id",),
            },
        ),
    ]
