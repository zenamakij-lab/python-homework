from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Book


@receiver(post_save, sender=Book)
@receiver(post_delete, sender=Book)
def invalidate_book_cache(sender, instance, **kwargs):
    cache.delete(f"book_detail:{instance.pk}")
    cache.clear()
