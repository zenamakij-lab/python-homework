import pytest
from django.urls import reverse

from tests.factories import BookFactory, UserFactory


@pytest.mark.django_db
class TestViews:
    def test_book_list_view_renders_books(self, client):
        BookFactory(title='Alpha', author='A1')
        response = client.get(reverse('books:list'))
        assert response.status_code == 200
        assert 'Alpha' in response.content.decode()

    def test_book_list_view_search_filters(self, client):
        BookFactory(title='One Book', author='John')
        BookFactory(title='Other Book', author='Jane')
        response = client.get(reverse('books:list'), {'search': 'One'})
        assert response.status_code == 200
        assert 'One Book' in response.content.decode()
        assert 'Other Book' not in response.content.decode()

    def test_book_detail_view_renders(self, client, book):
        response = client.get(reverse('books:detail', args=[book.pk]))
        assert response.status_code == 200
        assert book.title in response.content.decode()

    def test_add_to_cart_post(self, client, book):
        response = client.post(reverse('books:cart_add', args=[book.pk]), {'quantity': 2})
        assert response.status_code == 302
        session = client.session
        assert str(book.pk) in session['cart']

    def test_remove_from_cart_post(self, client, book):
        client.post(reverse('books:cart_add', args=[book.pk]), {'quantity': 2})
        response = client.post(reverse('books:cart_remove', args=[book.pk]))
        assert response.status_code == 302

    def test_clear_cart_post(self, client, book):
        client.post(reverse('books:cart_add', args=[book.pk]))
        response = client.post(reverse('books:cart_clear'))
        assert response.status_code == 302

    def test_cart_view_renders_items(self, client, book):
        client.post(reverse('books:cart_add', args=[book.pk]), {'quantity': 1})
        response = client.get(reverse('books:cart'))
        assert response.status_code == 200
        assert book.title in response.content.decode()

    def test_async_book_list_returns_json(self, client):
        BookFactory(title='Async Book')
        response = client.get('/async/')
        assert response.status_code == 200
        assert response.json()['count'] >= 1

    def test_async_book_detail_returns_data(self, client, book):
        response = client.get(f'/async/{book.pk}/')
        assert response.status_code == 200
        assert response.json()['title'] == book.title

    def test_async_cart_summary_returns_total(self, client, book):
        session = client.session
        session['cart'] = {str(book.pk): {'quantity': 2}}
        session.save()
        response = client.get('/async/cart/')
        assert response.status_code == 200
        assert response.json()['items'] == 1
