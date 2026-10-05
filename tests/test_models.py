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
        category = CategoryFactory(name='Fantasy', slug='fantasy')
        assert str(category) == 'Fantasy'

    def test_book_string_representation(self, book):
        assert str(book) == book.title

    def test_order_string_representation(self):
        order = OrderFactory()
        assert str(order) == f'Order #{order.pk}'

    def test_order_item_string_representation(self):
        item = OrderItemFactory()
        assert str(item) == f'{item.book.title} x {item.quantity}'

    def test_order_item_subtotal(self):
        item = OrderItemFactory(quantity=3, price=Decimal('12.50'))
        assert item.subtotal == Decimal('37.50')

    def test_user_manager_requires_email(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email='', password='pass')

    def test_user_manager_create_user(self):
        user = User.objects.create_user(email='user@example.com', username='user1', password='Pass1234!')
        assert user.email == 'user@example.com'
        assert user.check_password('Pass1234!')

    def test_user_manager_create_superuser(self):
        admin = User.objects.create_superuser(email='admin@example.com', username='admin', password='Pass1234!')
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_cart_add_increases_quantity(self, book, rf):
        request = rf.get('/')
        request.session = {}
        cart = Cart(request)
        cart.add(book, quantity=2)
        assert len(cart) == 2

    def test_cart_remove_deletes_item(self, book, rf):
        request = rf.get('/')
        request.session = {}
        cart = Cart(request)
        cart.add(book, quantity=3)
        cart.remove(book)
        assert list(cart.cart) == []

    def test_cart_clear_removes_all_items(self, book, rf):
        request = rf.get('/')
        request.session = {}
        cart = Cart(request)
        cart.add(book)
        cart.clear()
        assert cart.cart == {}

    def test_cart_total_price(self, book, rf):
        request = rf.get('/')
        request.session = {}
        cart = Cart(request)
        cart.add(book, quantity=2)
        assert cart.get_total_price() == book.price * 2
