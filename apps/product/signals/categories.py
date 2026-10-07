from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.product.models import Category


@receiver(pre_save, sender=Category)
def set_level_and_handle_parent_change(sender, instance, **kwargs):
    instance.level = instance.parent.level + 1 if instance.parent else 0

    if not instance.pk:
        return

    old = Category.objects.get(pk=instance.pk)
    if old.parent != instance.parent:
        if old.parent and not old.parent.children.exclude(pk=instance.pk).exists():
            Category.objects.filter(pk=old.parent.pk).update(is_leaf=True)

        if instance.parent:
            Category.objects.filter(pk=instance.parent.pk).update(is_leaf=False)


@receiver(post_save, sender=Category)
def update_is_leaf_on_save(sender, instance, created, **kwargs):
    if created:
        Category.objects.filter(pk=instance.pk).update(is_leaf=True)

        if instance.parent_id:
            Category.objects.filter(pk=instance.parent_id).update(is_leaf=False)


@receiver(post_delete, sender=Category)
def update_is_leaf_on_delete(sender, instance, **kwargs):
    if not instance.parent_id:
        return

    has_siblings = Category.objects.filter(parent_id=instance.parent_id).exists()
    if not has_siblings:
        Category.objects.filter(pk=instance.parent_id).update(is_leaf=True)


@receiver(post_save, sender=Category)
def deactivate_children(sender, instance, **kwargs):
    children = Category.objects.filter(parent=instance)
    for child in children:
        child.is_active = instance.is_active
        child.save()
