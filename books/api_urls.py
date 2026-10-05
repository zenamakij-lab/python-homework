from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import BookViewSet, CartViewSet, CategoryViewSet, OrderViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]
