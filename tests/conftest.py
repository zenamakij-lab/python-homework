import pytest
from django.test import Client

from .factories import BookFactory, CategoryFactory, UserFactory


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def category():
    return CategoryFactory()


@pytest.fixture
def book(category):
    return BookFactory(category=category)


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def staff_user():
    return UserFactory(is_staff=True, is_superuser=True)
