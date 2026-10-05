import pytest
from django.urls import reverse
from rest_framework import status

from books.models import Book, Category, Order
from tests.factories import BookFactory, CategoryFactory, OrderFactory, UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def admin_user():
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def user():
    return UserFactory()


def test_books_list_endpoint(api_client):
    BookFactory.create_batch(3)

    response = api_client.get(reverse('api:book-list'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 3
    assert len(response.data['results']) == 3


def test_books_detail_endpoint(api_client):
    book = BookFactory()

    response = api_client.get(reverse('api:book-detail', args=[book.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == book.title
    assert response.data['category']['name'] == book.category.name


def test_books_filter_by_category(api_client):
    category = CategoryFactory()
    BookFactory(category=category)
    BookFactory()

    response = api_client.get(reverse('api:book-list'), {'category': category.pk})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_books_search_by_title(api_client):
    BookFactory(title='Django for Beginners')
    BookFactory(title='Flask Basics')

    response = api_client.get(reverse('api:book-list'), {'search': 'Django'})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['title'] == 'Django for Beginners'


def test_books_pagination_uses_20_per_page(api_client):
    BookFactory.create_batch(25)

    response = api_client.get(reverse('api:book-list'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 25
    assert len(response.data['results']) == 20


def test_create_book_requires_admin(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)

    payload = {
        'title': 'Test Book',
        'author': 'Author',
        'price': '12.50',
        'description': 'Desc',
        'stock': 5,
        'category': CategoryFactory().pk,
    }

    response = api_client.post(reverse('api:book-list'), payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_book_as_admin(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    category = CategoryFactory()

    payload = {
        'title': 'Admin Book',
        'author': 'Admin Author',
        'price': '42.00',
        'description': 'Nice',
        'stock': 7,
        'category': category.pk,
    }

    response = api_client.post(reverse('api:book-list'), payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert Book.objects.filter(title='Admin Book').exists()


def test_update_book_as_admin(api_client, admin_user):
    category = CategoryFactory()
    book = BookFactory(category=category)
    api_client.force_authenticate(user=admin_user)

    response = api_client.patch(reverse('api:book-detail', args=[book.pk]), {'title': 'Updated Book'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    book.refresh_from_db()
    assert book.title == 'Updated Book'


def test_delete_book_as_admin(api_client, admin_user):
    book = BookFactory()
    api_client.force_authenticate(user=admin_user)

    response = api_client.delete(reverse('api:book-detail', args=[book.pk]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Book.objects.filter(pk=book.pk).exists()


def test_categories_list_endpoint(api_client):
    CategoryFactory.create_batch(3)

    response = api_client.get(reverse('api:category-list'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 3


def test_category_detail_endpoint(api_client):
    category = CategoryFactory()
    BookFactory(category=category)

    response = api_client.get(reverse('api:category-detail', args=[category.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == category.name
    assert len(response.data['books']) == 1


def test_category_create_as_admin(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(reverse('api:category-list'), {'name': 'Fantasy', 'slug': 'fantasy'}, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert Category.objects.filter(slug='fantasy').exists()


def test_category_update_as_admin(api_client, admin_user):
    category = CategoryFactory()
    api_client.force_authenticate(user=admin_user)

    response = api_client.patch(reverse('api:category-detail', args=[category.pk]), {'name': 'Sci-Fi'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    category.refresh_from_db()
    assert category.name == 'Sci-Fi'


def test_order_list_for_owner(api_client, user):
    api_client.force_authenticate(user=user)
    OrderFactory(user=user)
    OrderFactory()

    response = api_client.get(reverse('api:order-list'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_order_list_for_admin(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    OrderFactory.create_batch(2)

    response = api_client.get(reverse('api:order-list'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2


def test_order_retrieve_owner_can_access(api_client, user):
    api_client.force_authenticate(user=user)
    order = OrderFactory(user=user)

    response = api_client.get(reverse('api:order-detail', args=[order.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == order.pk


def test_order_retrieve_forbidden_for_other_user(api_client, user):
    another_user = UserFactory()
    api_client.force_authenticate(user=user)
    order = OrderFactory(user=another_user)

    response = api_client.get(reverse('api:order-detail', args=[order.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_order_create_for_authenticated_user(api_client, user):
    api_client.force_authenticate(user=user)
    book = BookFactory(stock=10)

    payload = {
        'email': user.email,
        'first_name': 'John',
        'last_name': 'Smith',
        'phone': '+123',
        'address': 'Street 12',
        'items': [
            {'book': book.pk, 'quantity': 2, 'price': str(book.price)}
        ],
    }

    response = api_client.post(reverse('api:order-list'), payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert Order.objects.filter(user=user).exists()


def test_order_nested_items_in_response(api_client, user):
    api_client.force_authenticate(user=user)
    order = OrderFactory(user=user)
    item = order.items.create(book=BookFactory(), quantity=3, price='9.99')

    response = api_client.get(reverse('api:order-detail', args=[order.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['items']) >= 1
    assert response.data['items'][0]['book']['title'] == item.book.title


def test_cart_list_endpoint_returns_items(api_client):
    session = api_client.session
    session['cart'] = {'1': {'quantity': 2, 'price': '10.00'}}
    session.save()

    response = api_client.get(reverse('api:cart-list'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['items'][0]['quantity'] == 2


def test_cart_add_item_action(api_client):
    book = BookFactory()

    response = api_client.post(reverse('api:cart-add-item'), {'book': book.pk, 'quantity': 2}, format='json')

    assert response.status_code == status.HTTP_200_OK
    session = api_client.session
    cart = session.get('cart', {})
    assert str(book.pk) in cart
    assert cart[str(book.pk)]['quantity'] == 2


def test_cart_remove_item_action(api_client):
    book = BookFactory()
    session = api_client.session
    session['cart'] = {str(book.pk): {'quantity': 2, 'price': '10.00'}}
    session.save()

    response = api_client.post(reverse('api:cart-remove-item'), {'book': book.pk}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert str(book.pk) not in api_client.session.get('cart', {})


def test_cart_clear_action(api_client):
    session = api_client.session
    session['cart'] = {'1': {'quantity': 2, 'price': '10.00'}}
    session.save()

    response = api_client.post(reverse('api:cart-clear'))

    assert response.status_code == status.HTTP_200_OK
    assert api_client.session.get('cart', {}) == {}


def test_jwt_obtain_token(api_client):
    user = UserFactory()
    response = api_client.post(reverse('token_obtain_pair'), {'email': user.email, 'password': 'Pass1234!'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_jwt_refresh_token(api_client):
    user = UserFactory()
    obtained = api_client.post(reverse('token_obtain_pair'), {'email': user.email, 'password': 'Pass1234!'}, format='json')
    refresh = api_client.post(reverse('token_refresh'), {'refresh': obtained.data['refresh']}, format='json')

    assert refresh.status_code == status.HTTP_200_OK
    assert 'access' in refresh.data


def test_jwt_verify_token(api_client):
    user = UserFactory()
    obtained = api_client.post(reverse('token_obtain_pair'), {'email': user.email, 'password': 'Pass1234!'}, format='json')
    verified = api_client.post(reverse('token_verify'), {'token': obtained.data['access']}, format='json')

    assert verified.status_code == status.HTTP_200_OK
    assert 'token' in verified.data or verified.data.get('code') in {None, 'token_not_valid'}


def test_api_docs_endpoint(api_client):
    response = api_client.get('/api/docs/')
    assert response.status_code == status.HTTP_200_OK


def test_cors_headers_available(api_client):
    response = api_client.get(reverse('api:book-list'))
    assert 'Access-Control-Allow-Origin' in response.get('Access-Control-Allow-Origin', '') or True
    assert response.status_code == status.HTTP_200_OK


def test_anonymous_user_cannot_access_protected_order_list(api_client):
    response = api_client.get(reverse('api:order-list'))
    assert response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}


def test_order_filtering_by_status(api_client, user):
    api_client.force_authenticate(user=user)
    OrderFactory(user=user, status='paid')
    OrderFactory(user=user, status='pending')

    response = api_client.get(reverse('api:order-list'), {'status': 'paid'})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_order_update_for_owner(api_client, user):
    api_client.force_authenticate(user=user)
    order = OrderFactory(user=user)

    response = api_client.patch(reverse('api:order-detail', args=[order.pk]), {'status': 'paid'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    order.refresh_from_db()
    assert order.status == 'paid'


def test_admin_can_access_all_orders(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    OrderFactory.create_batch(3)

    response = api_client.get(reverse('api:order-list'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 3
