from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import Category, Product, ProductImage


class ProductRepository:
    def get_products(self, only_active=True):
        qs = Product.objects.select_related("unit", "category").prefetch_related(
            "images",
            "characteristics",
            "product_attribute_values__attribute",
            "product_attribute_values__attribute_value",
        )
        if only_active:
            qs = qs.filter(is_active=True)
        return qs

    def get_product(self, product_id, only_active=True):
        product = (
            self.get_products(only_active=only_active)
            .prefetch_related(
                "product_attribute_values__attribute",
                "product_attribute_values__attribute_value",
            )
            .filter(id=product_id)
            .first()
        )
        if not product:
            raise ObjectNotFoundException(
                message="Product not found", message_key="product_not_found"
            )

        return product

    def get_image(self, product_id, image_id):
        image = ProductImage.objects.filter(id=image_id, product_id=product_id).first()
        if not image:
            raise ObjectNotFoundException(
                message="Image not found", message_key="product_image_not_found"
            )
        return image

    def add_images(self, product, files):
        position = product.images.count()
        return ProductImage.objects.bulk_create(
            [
                ProductImage(product=product, file=file, position=position + index)
                for index, file in enumerate(files)
            ]
        )

    def get_all_items(self, search):
        products = self.get_products()
        categories = Category.objects.filter(is_active=True)
        if search:
            products = products.filter(name__icontains=search)
            categories = categories.filter(name__icontains=search)
        return {"products": products[:5], "categories": categories[:5]}
