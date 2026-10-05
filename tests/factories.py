from decimal import Decimal
from uuid import uuid4

import factory
from django.contrib.auth import get_user_model

from books.models import Book, Category, Order, OrderItem

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user-{uuid4().hex[:8]}-{n}')
    email = factory.Sequence(lambda n: f'user-{uuid4().hex[:8]}-{n}@example.com')
    first_name = 'Test'
    last_name = 'User'
    password = factory.PostGenerationMethodCall('set_password', 'Pass1234!')


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.Sequence(lambda n: f'category-{uuid4().hex[:8]}-{n}')


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f'Book {n}')
    author = factory.Sequence(lambda n: f'Author {n}')
    price = Decimal('19.99')
    description = 'Test description'
    stock = 10
    category = factory.SubFactory(CategoryFactory)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    email = factory.SelfAttribute('user.email')
    first_name = 'Jane'
    last_name = 'Doe'
    phone = '+123456789'
    address = 'Main Street 1'
    status = Order.STATUS_PENDING
    total_price = Decimal('25.00')


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    book = factory.SubFactory(BookFactory)
    quantity = 2
    price = factory.LazyAttribute(lambda obj: obj.book.price)
