from collections import defaultdict

from django.db.models import Case, CharField, Count, IntegerField, Value, When

from apps.catalog.models import Category, Product

PATH_SEPARATOR = " › "


class CategoryTree:
    """Whole category tree loaded with one query.

    Kategoriyalar soni bir necha yuzta, shuning uchun daraxtni Python da
    yig'ish rekursiv SQL dan sodda va bazaga bog'liq emas.
    """

    def __init__(self, categories, product_counts=None):
        self.nodes = {category.pk: category for category in categories}
        self.children = defaultdict(list)
        for category in categories:
            self.children[category.parent_id].append(category)
        for siblings in self.children.values():
            siblings.sort(key=lambda category: (category.order, category.pk))
        self.product_counts = product_counts or {}
        self._branch_counts = {}

    @classmethod
    def load(cls, active_products_only=True, queryset=None):
        products = Product.objects.all()
        if active_products_only:
            products = products.filter(is_active=True)
        product_counts = dict(
            products.values("category_id")
            .annotate(count=Count("id"))
            .values_list("category_id", "count")
        )
        categories = Category.objects.all() if queryset is None else queryset
        return cls(list(categories), product_counts)

    @property
    def roots(self):
        return self.children.get(None, [])

    def get_children(self, category_id):
        return self.children.get(category_id, [])

    def is_leaf(self, category_id):
        return not self.children.get(category_id)

    def get_path(self, category_id):
        """Categories from the root down to the category itself."""
        path = []
        current = self.nodes.get(category_id)
        while current is not None:
            path.append(current)
            current = self.nodes.get(current.parent_id)
        return path[::-1]

    def get_label(self, category_id):
        return PATH_SEPARATOR.join(category.name for category in self.get_path(category_id))

    def find(self, slugs):
        """Category at the URL path `slugs` (["consumables", "fasteners"]), or None."""
        found = None
        for slug in slugs:
            found = next(
                (child for child in self.get_children(found.pk if found else None) if child.slug == slug),
                None,
            )
            if found is None:
                return None
        return found

    def get_slugs(self, category_id):
        return [category.slug for category in self.get_path(category_id)]

    def get_descendant_ids(self, category_id):
        """The category and every category below it."""
        ids = [category_id]
        stack = [category_id]
        while stack:
            for child in self.get_children(stack.pop()):
                ids.append(child.pk)
                stack.append(child.pk)
        return ids

    def get_branch_count(self, category_id):
        """Products in the category and in every category below it."""
        if category_id not in self._branch_counts:
            self._branch_counts[category_id] = self.product_counts.get(category_id, 0) + sum(
                self.get_branch_count(child.pk) for child in self.get_children(category_id)
            )
        return self._branch_counts[category_id]

    def walk(self):
        """Depth-first `(category, depth)` pairs in display order."""
        stack = [(category, 0) for category in reversed(self.roots)]
        while stack:
            category, depth = stack.pop()
            yield category, depth
            stack.extend((child, depth + 1) for child in reversed(self.get_children(category.pk)))

    def position_expression(self, field="pk"):
        """SQL expression that orders rows by their place in the tree."""
        whens = [
            When(**{field: category.pk}, then=Value(position))
            for position, (category, _) in enumerate(self.walk())
        ]
        return Case(*whens, default=Value(len(self.nodes)), output_field=IntegerField())

    def depth_expression(self, field="pk"):
        whens = [When(**{field: category.pk}, then=Value(depth)) for category, depth in self.walk()]
        return Case(*whens, default=Value(0), output_field=IntegerField())

    def label_expression(self, field="pk", ids=None):
        whens = [
            When(**{field: category_id}, then=Value(self.get_label(category_id)))
            for category_id in (self.nodes if ids is None else ids)
            if category_id in self.nodes
        ]
        return Case(*whens, default=Value(""), output_field=CharField())

    def branch_count_expression(self, field="pk"):
        whens = [
            When(**{field: category_id}, then=Value(self.get_branch_count(category_id)))
            for category_id in self.nodes
        ]
        return Case(*whens, default=Value(0), output_field=IntegerField())

    def direct_count_expression(self, field="pk"):
        whens = [
            When(**{field: category_id}, then=Value(count))
            for category_id, count in self.product_counts.items()
            if count
        ]
        return Case(*whens, default=Value(0), output_field=IntegerField())
