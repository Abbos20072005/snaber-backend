from django.db import migrations


def wipe_catalog(apps, schema_editor):
    # Products are now flat (no variants / constructors); the demo catalog is
    # reseeded with `seed_building_materials`.
    for model in (
        "CartItem",
        "Favourite",
        "VariantAttributeStockConstructor",
        "VariantMediaConstructor",
        "ProductAttributeValueConstructor",
        "CharacteristicConstructor",
        "VariantConstructor",
        "ProductConstructor",
        "Product",
    ):
        apps.get_model("product", model).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0025_remove_product_type_and_cart_rfq"),
        ("order", "0013_wipe_orders"),
        ("review", "0002_wipe_comments"),
        ("chat", "0003_alter_conversation_buyer_alter_conversation_seller_and_more"),
    ]

    operations = [
        migrations.RunPython(wipe_catalog, migrations.RunPython.noop),
    ]
