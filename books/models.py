from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    author = models.CharField(_('Author'), max_length=200)
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    description = models.TextField(_('Description'))
    stock = models.PositiveIntegerField(_('Stock'), default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name=_('Category'),
    )

    def __str__(self):
        return self.title


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    email = models.EmailField(_('Email'))
    first_name = models.CharField(_('First name'), max_length=100, blank=True)
    last_name = models.CharField(_('Last name'), max_length=100, blank=True)
    phone = models.CharField(_('Phone'), max_length=30, blank=True)
    address = models.TextField(_('Address'), blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total_price = models.DecimalField(_('Total price'), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    stripe_checkout_id = models.CharField(_('Stripe checkout id'), max_length=255, blank=True, default='')
    stripe_payment_intent_id = models.CharField(_('Stripe payment intent id'), max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Order #{self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_('Order'))
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='order_items', verbose_name=_('Book'))
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    price = models.DecimalField(_('Price'), max_digits=12, decimal_places=2)

    class Meta:
        ordering = ('id',)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.book.title} x {self.quantity}'