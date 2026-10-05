from decimal import Decimal
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from books.models import Order
from tests.factories import BookFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserFlows:
    def test_user_registration_flow(self, client):
        response = client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }, follow=True)
        assert response.status_code == 200
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_user_login_flow(self, client):
        user = UserFactory(username='loginuser', email='loginuser@example.com')
        user.set_password('Pass1234!')
        user.save()
        response = client.post(reverse('users:login'), {
            'username': 'loginuser@example.com',
            'password': 'Pass1234!',
        }, follow=True)
        assert response.status_code == 200
        assert response.wsgi_request.user.is_authenticated

    def test_logout_flow(self, client, user):
        client.force_login(user)
        response = client.post(reverse('users:logout'), follow=True)
        assert response.status_code == 200

    def test_profile_requires_auth(self, client):
        response = client.get(reverse('users:profile'))
        assert response.status_code == 302

    def test_profile_page_for_logged_user(self, client, user):
        client.force_login(user)
        response = client.get(reverse('users:profile'))
        assert response.status_code == 200

    def test_book_list_page_has_title(self, client):
        response = client.get(reverse('books:list'))
        assert response.status_code == 200
        assert 'Книги' in response.content.decode() or 'Books' in response.content.decode()

    def test_book_search_flow(self, client):
        BookFactory(title='Search Me', author='Alice')
        response = client.get(reverse('books:list'), {'search': 'search'})
        assert response.status_code == 200
        assert 'Search Me' in response.content.decode()

    def test_cart_flow_add_and_clear(self, client, book):
        client.post(reverse('books:cart_add', args=[book.pk]), {'quantity': 2})
        assert client.session['cart'][str(book.pk)]['quantity'] == 2
        client.post(reverse('books:cart_clear'))
        assert client.session['cart'] == {}

    def test_checkout_requires_cart(self, client):
        response = client.post(reverse('books:checkout'))
        assert response.status_code == 400

    @mock.patch('books.views.stripe.checkout.Session.create')
    @mock.patch('books.views.send_mail')
    def test_checkout_creates_order_and_redirects(self, send_mail_mock, stripe_mock, client, book):
        stripe_mock.return_value = mock.Mock(id='sess_123', url='https://example.com/checkout')
        client.post(reverse('books:cart_add', args=[book.pk]), {'quantity': 1})
        response = client.post(reverse('books:checkout'), {'email': 'buyer@example.com'}, follow=False)
        assert response.status_code == 302
        assert Order.objects.filter(email='buyer@example.com').exists()
        send_mail_mock.assert_called_once()

    @mock.patch('books.views.stripe.checkout.Session.create')
    def test_checkout_without_stripe_key_returns_error(self, stripe_mock, settings, client, book):
        settings.STRIPE_SECRET_KEY = ''
        client.post(reverse('books:cart_add', args=[book.pk]), {'quantity': 1})
        response = client.post(reverse('books:checkout'), {'email': 'buyer@example.com'})
        assert response.status_code == 400
        stripe_mock.assert_not_called()

    @mock.patch('books.views.stripe.checkout.Session.retrieve')
    def test_checkout_success_sets_order_paid(self, retrieve_mock, client, book):
        order = Order.objects.create(email='paid@example.com', total_price=Decimal('12.00'))
        retrieve_mock.return_value = mock.Mock(
            metadata={'order_id': str(order.pk)},
            payment_status='paid',
            payment_intent='pi_123',
        )
        response = client.get(reverse('books:checkout_success') + '?session_id=cs_test_123')
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == Order.STATUS_PAID

    def test_checkout_cancel_page(self, client):
        response = client.get(reverse('books:checkout_cancel'))
        assert response.status_code == 200

    def test_async_book_list_endpoint(self, client):
        BookFactory(title='A1')
        response = client.get('/async/')
        assert response.status_code == 200
        assert response.json()['count'] >= 1

    def test_async_book_detail_endpoint(self, client, book):
        response = client.get(f'/async/{book.pk}/')
        assert response.status_code == 200
        assert response.json()['title'] == book.title

    def test_async_cart_summary_endpoint(self, client, book):
        session = client.session
        session['cart'] = {str(book.pk): {'quantity': 2}}
        session.save()
        response = client.get('/async/cart/')
        assert response.status_code == 200
        assert response.json()['items'] == 1

    def test_register_redirects_to_login(self, client):
        response = client.post(reverse('users:register'), {
            'username': 'reguser',
            'email': 'reguser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }, follow=True)
        assert response.redirect_chain

    def test_admin_login_page_is_accessible(self, client):
        response = client.get('/admin/login/')
        assert response.status_code == 200

    def test_book_store_has_no_error_page(self, client):
        response = client.get(reverse('books:list'))
        assert response.status_code != 500

    def test_order_total_is_saved(self, client, book):
        client.post(reverse('books:cart_add', args=[book.pk]), {'quantity': 2})
        with mock.patch('books.views.send_mail') as send_mail_mock, mock.patch('books.views.stripe.checkout.Session.create') as stripe_mock:
            stripe_mock.return_value = mock.Mock(id='sess_456', url='https://example.com/checkout')
            client.post(reverse('books:checkout'), {'email': 'total@example.com'})
            order = Order.objects.get(email='total@example.com')
            assert order.total_price == book.price * 2
            send_mail_mock.assert_called_once()
