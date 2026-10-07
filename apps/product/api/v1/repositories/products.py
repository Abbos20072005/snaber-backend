from apps.company.models import Company
from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import Category, Product, Variant


class ProductRepository:
    def get_products(self, company=None):
        qs = Product.objects.filter(is_active=True)
        if company:
            qs = qs.filter(owner=company)
        return qs

    def get_product(self, product_id):
        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            raise ObjectNotFoundException(
                message="Product not found", message_key="product_not_found"
            )

        return product

    def get_draft_product(self, product_id):
        product = Product.objects.filter(
            id=product_id,
        ).first()
        if not product:
            raise ObjectNotFoundException(
                message="Product not found", message_key="product_not_found"
            )
        return product

    def get_all_items(self, search):
        if search:
            products = Variant.objects.filter(
                product__name__icontains=search,
                is_active=True,
            )[:5]
            categories = Category.objects.filter(
                name__icontains=search, is_active=True
            )[:5]
            companies = Company.objects.filter(
                name__icontains=search, status=Company.CompanyStatus.ACTIVE
            )[:5]
        else:
            products = Variant.objects.filter(is_active=True)[:5]
            categories = Category.objects.filter(is_active=True)[:5]
            companies = Company.objects.filter(status=Company.CompanyStatus.ACTIVE)[:5]
        return {
            "products": products,
            "categories": categories,
            "companies": companies,
        }
