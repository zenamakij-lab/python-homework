from django.urls import path

from .views import (
    BookCreateView,
    BookDeleteView,
    BookDetailView,
    BookListView,
    BookUpdateView,
    add_to_cart,
    async_book_detail,
    async_book_list,
    async_cart_summary,
    cart_view,
    checkout_cancel,
    checkout_success,
    checkout_view,
    clear_cart,
    remove_from_cart,
)

app_name = 'books'

urlpatterns = [
    path('', BookListView.as_view(), name='list'),
    path('async/', async_book_list, name='async_list'),
    path('async/<int:pk>/', async_book_detail, name='async_detail'),
    path('async/cart/', async_cart_summary, name='async_cart'),
    path('create/', BookCreateView.as_view(), name='create'),
    path('cart/', cart_view, name='cart'),
    path('cart/add/<int:book_id>/', add_to_cart, name='cart_add'),
    path('cart/remove/<int:book_id>/', remove_from_cart, name='cart_remove'),
    path('cart/clear/', clear_cart, name='cart_clear'),
    path('checkout/', checkout_view, name='checkout'),
    path('checkout/success/', checkout_success, name='checkout_success'),
    path('checkout/cancel/', checkout_cancel, name='checkout_cancel'),
    path('<int:pk>/', BookDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', BookUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', BookDeleteView.as_view(), name='delete'),
]