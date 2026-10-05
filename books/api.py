from decimal import Decimal

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, BasePermission, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .cart import Cart
from .models import Book, Category, Order, OrderItem


class IsOwnerOrReadOnly(BasePermission):
    message = 'You can only modify your own orders.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_staff or getattr(obj, 'user', None) == request.user
        if request.user.is_staff:
            return True
        return getattr(obj, 'user', None) == request.user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class BookSummarySerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'category']


class CategorySerializer(serializers.ModelSerializer):
    books = BookSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'books']


class BookSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'description', 'stock', 'category']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = CategorySerializer(instance.category).data
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'quantity', 'price', 'subtotal']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['book'] = BookSummarySerializer(instance.book).data
        return data


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'email',
            'first_name',
            'last_name',
            'phone',
            'address',
            'status',
            'total_price',
            'stripe_checkout_id',
            'created_at',
            'updated_at',
            'items',
        ]
        read_only_fields = ['user', 'total_price', 'stripe_checkout_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None

        order = Order.objects.create(
            user=user,
            email=validated_data.get('email', user.email if user else ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
            status=validated_data.get('status', Order.STATUS_PENDING),
        )

        total_price = Decimal('0.00')
        for item_data in self.initial_data.get('items', []):
            book_id = item_data.get('book')
            book = get_object_or_404(Book, pk=book_id)
            quantity = int(item_data.get('quantity', 1))
            if quantity <= 0:
                raise serializers.ValidationError({'items': 'Quantity must be greater than zero.'})
            if quantity > book.stock:
                raise serializers.ValidationError({'items': f'Not enough stock for {book.title}.'})

            price = Decimal(str(item_data.get('price', book.price)))
            OrderItem.objects.create(order=order, book=book, quantity=quantity, price=price)
            total_price += price * quantity

        order.total_price = total_price
        order.save(update_fields=['total_price'])
        return order


class BookFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='category__id')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Book
        fields = ['category', 'author', 'min_price', 'max_price']

    @property
    def qs(self):
        parent = super().qs
        search = self.request.GET.get('search', '').strip()
        if search:
            parent = parent.filter(Q(title__icontains=search) | Q(author__icontains=search))
        return parent


class OrderFilter(filters.FilterSet):
    class Meta:
        model = Order
        fields = ['status', 'email', 'user']


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('category').all().order_by('title')
    serializer_class = BookSerializer
    filterset_class = BookFilter
    search_fields = ['title', 'author']
    ordering_fields = ['title', 'price']

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(author__icontains=search))
        return qs


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.prefetch_related('books').all().order_by('name')
    serializer_class = CategorySerializer
    search_fields = ['name', 'slug']
    ordering_fields = ['name']

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [IsAdminUser()]
        return [AllowAny()]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('user').prefetch_related('items__book').all().order_by('-created_at')
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'total_price']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def get_object(self):
        queryset = Order.objects.select_related('user').prefetch_related('items__book').all()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        obj = get_object_or_404(queryset, **{self.lookup_field: lookup_value})
        self.check_object_permissions(self.request, obj)
        return obj

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        cart = Cart(request)
        return Response(self._cart_payload(cart))

    @action(detail=False, methods=['post'], url_path='add-item')
    def add_item(self, request):
        book = get_object_or_404(Book, pk=request.data.get('book'))
        quantity = int(request.data.get('quantity', 1))
        if quantity <= 0:
            return Response({'detail': 'Quantity must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart(request)
        cart.add(book, quantity=quantity)
        return Response(self._cart_payload(cart))

    @action(detail=False, methods=['post'], url_path='remove-item')
    def remove_item(self, request):
        book = get_object_or_404(Book, pk=request.data.get('book'))
        cart = Cart(request)
        cart.remove(book)
        return Response(self._cart_payload(cart))

    @action(detail=False, methods=['post'], url_path='clear')
    def clear(self, request):
        cart = Cart(request)
        cart.clear()
        return Response(self._cart_payload(cart))

    def _cart_payload(self, cart):
        items = []
        for item_key, item in cart.cart.items():
            quantity = int(item.get('quantity', 0))
            price_value = item.get('price', '0.00')
            item_total = Decimal(str(price_value)) * quantity
            book = None
            try:
                book = Book.objects.get(pk=int(item_key))
            except Book.DoesNotExist:
                book = None

            if book is not None:
                item_payload = {
                    'book': {
                        'id': book.id,
                        'title': book.title,
                        'author': book.author,
                        'price': str(book.price),
                    },
                    'quantity': quantity,
                    'price': str(book.price),
                    'total_price': str(item_total),
                }
            else:
                item_payload = {
                    'book_id': int(item_key),
                    'quantity': quantity,
                    'price': str(price_value),
                    'total_price': str(item_total),
                }
            items.append(item_payload)

        return {
            'items': items,
            'total_items': len(cart),
            'total_price': str(cart.get_total_price()),
        }
