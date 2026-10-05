from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from books.cart import Cart
from books.models import Book, Category, Order, OrderItem
from tests.factories import BookFactory, CategoryFactory, OrderFactory, OrderItemFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestModels:
    def test_category_string_representation(self):
        # Generated with AI, reviewed and modified
        category = CategoryFactory(name='Fantasy', slug='fantasy')
        assert str(category) == 'Fantasy'

    def test_book_string_representation(self, book):
        # Generated with AI, reviewed and modified
        assert str(book) == book.title

    def test_order_string_representation(self):
        # Generated with AI, reviewed and modified
        order = OrderFactory()
        assert str(order) == f'Order #{order.pk}'

    def test_order_item_string_representation(self):
        # Generated with AI, reviewed and modified
        item = OrderItemFactory()
        assert str(item) == f'{item.book.title} x {item.quantity}'

    def test_order_item_subtotal(self):
        # Generated with AI, reviewed and modified
        item = OrderItemFactory(quantity=3, price=Decimal('12.50'))
        assert item.subtotal == Decimal('37.50')

    def test_user_manager_requires_email(self):
        # Generated with AI, reviewed and modified
        with pytest.raises(ValueError):
            User.objects.create_user(email='', password='pass')

    def test_user_manager_create_user(self):
        # Generated with AI, reviewed and modified
        user = User.objects.create_user(email='user@example.com', username='user1', password='Pass1234!')
        assert user.email == 'user@example.com'
        assert user.check_password('Pass1234!')

    def test_user_manager_create_superuser(self):
        # Generated with AI, reviewed and modified
        admin = User.objects.create_superuser(email='admin@example.com', username='admin', password='Pass1234!')
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_cart_add_increases_quantity(self, book, rf):
        # Generated with AI, reviewed and modified
        request = rf.get('/')
        request.session = {}
        cart = Cart(request)
        cart.add(book, quantity=2)
        assert len(cart) == 2

    def test_cart_remove_deletes_item(self, book, rf):
        # Generated with AI, reviewed and modified
        request = rf.get('/')
        request.session = {}
        cart = Cart(request)
        cart.add(book, quantity=3)
        cart.remove(book)
        assert list(cart.cart) == []

    def test_cart_clear_removes_all_items(self, book, rf):
        # Generated with AI, reviewed and modified
        request = rf.get('/')
        request.session = {}
        cart = Cart(request)
        cart.add(book)
        cart.clear()
        assert cart.cart == {}

    def test_cart_total_price(self, book, rf):
        # Generated with AI, reviewed and modified
        request = rf.get('/')
        request.session = {}
        cart = Cart(request)
        cart.add(book, quantity=2)
        assert cart.get_total_price() == book.price * 2
