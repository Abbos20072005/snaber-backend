from rest_framework import serializers

from apps.product.models import ProductAttributeValue


def field_error(field, code, message):
    """A field error with a stable code, the frontend translates the code."""
    return serializers.ValidationError(
        {field: [serializers.ErrorDetail(message, code=code)]}
    )


def validate_variant_options(family, attribute_values, exclude_product_id=None):
    """Check the option values of one variant against the axes of its family.

    A variant picks at most one value per axis, and two variants of a family can't
    share the same full combination of values.
    """
    axes = list(family.axes.all())
    axis_ids = [axis.id for axis in axes]

    picked = {}
    for value in attribute_values:
        if value.attribute_id not in axis_ids:
            continue
        if value.attribute_id in picked:
            axis = next(axis for axis in axes if axis.id == value.attribute_id)
            raise field_error(
                "attribute_values",
                "variant_axis_multiple",
                f"Pick only one value for «{axis.name}».",
            )
        picked[value.attribute_id] = value.id

    combination = tuple(picked.get(axis_id) for axis_id in axis_ids)
    if not axis_ids or None in combination:
        return

    siblings = {}
    rows = ProductAttributeValue.objects.filter(
        product__family=family, attribute_id__in=axis_ids
    ).values_list("product_id", "attribute_id", "attribute_value_id")
    for product_id, attribute_id, value_id in rows:
        if product_id != exclude_product_id:
            siblings.setdefault(product_id, {})[attribute_id] = value_id

    for sibling in siblings.values():
        if tuple(sibling.get(axis_id) for axis_id in axis_ids) == combination:
            raise field_error(
                "attribute_values",
                "variant_options_duplicate",
                "A variant with these options already exists.",
            )
