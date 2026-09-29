from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    if sender.name not in {'users', 'books'}:
        return

    customer_group, _ = Group.objects.get_or_create(name='Customers')
    customer_group.permissions.set(
        Permission.objects.filter(codename__in=['view_book', 'view_category'])
    )

    manager_group, _ = Group.objects.get_or_create(name='Managers')
    manager_group.permissions.set(
        Permission.objects.filter(
            codename__in=[
                'add_book', 'change_book', 'view_book', 'delete_book',
                'add_category', 'change_category', 'view_category', 'delete_category',
            ]
        )
    )
