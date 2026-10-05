from decimal import Decimal

import stripe
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .cart import Cart
from .models import Book, Order, OrderItem


def send_order_confirmation(order):
    subject = f'Order #{order.pk} confirmation'
    message = (
        f'Thank you for your order #{order.pk}.\n'
        f'Email: {order.email}\n'
        f'Total: {order.total_price}\n'
        f'Status: {order.get_status_display()}'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email], fail_silently=False)


def create_order_from_cart(request, cart):
    if not cart.cart:
        raise ValueError('Cart is empty.')

    email = request.POST.get('email') or (request.user.email if request.user.is_authenticated else '')
    if not email:
        raise ValueError('Email is required.')

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=email,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
        )

        total_price = Decimal('0.00')

        for item in cart:
            book = item['book']
            quantity = int(item['quantity'])

            if quantity > book.stock:
                raise ValueError(f'Not enough stock for {book.title}.')

            price = Decimal(str(book.price))
            OrderItem.objects.create(order=order, book=book, quantity=quantity, price=price)
            total_price += price * quantity

            Book.objects.filter(pk=book.pk).update(stock=F('stock') - quantity)

        order.total_price = total_price
        order.save(update_fields=['total_price'])
        cart.clear()
        send_order_confirmation(order)
        return order


@require_POST
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    quantity = max(1, int(request.POST.get('quantity', 1)))
    cart = Cart(request)
    cart.add(book, quantity=quantity)
    return redirect('books:list')


@require_POST
def remove_from_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    cart = Cart(request)
    cart.remove(book)
    return redirect('books:cart')


@require_POST
def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    return redirect('books:cart')


def cart_view(request):
    cart = Cart(request)
    items = list(cart)
    total_price = cart.get_total_price()
    body = [
        '<h2>Cart</h2>',
        f'<p>Items: {len(items)}</p>',
        f'<p>Total: {total_price}</p>',
    ]
    for item in items:
        book = item['book']
        body.append(f'<p>{book.title} x {item["quantity"]} = {item["total_price"]}</p>')
    return HttpResponse(''.join(body))


@require_POST
def checkout_view(request):
    cart = Cart(request)
    if not cart.cart:
        return HttpResponseBadRequest('Cart is empty.')

    if not settings.STRIPE_SECRET_KEY:
        return HttpResponseBadRequest('Stripe secret key is not configured.')

    try:
        order = create_order_from_cart(request, cart)
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))

    stripe.api_key = settings.STRIPE_SECRET_KEY
    line_items = []
    for item in order.items.select_related('book').all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(item.price * 100),
                'product_data': {'name': item.book.title},
            },
            'quantity': item.quantity,
        })

    session = stripe.checkout.Session.create(
        mode='payment',
        line_items=line_items,
        customer_email=order.email,
        success_url=request.build_absolute_uri(reverse('books:checkout_success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('books:checkout_cancel')),
        metadata={'order_id': str(order.pk)},
    )

    order.stripe_checkout_id = session.id
    order.save(update_fields=['stripe_checkout_id'])
    return redirect(session.url, permanent=False)


def checkout_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return HttpResponse('Missing session_id.')

    if settings.STRIPE_SECRET_KEY:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        order_id = session.metadata.get('order_id')
        if order_id:
            order = get_object_or_404(Order, pk=order_id)
            if session.payment_status == 'paid':
                order.status = Order.STATUS_PAID
                order.stripe_payment_intent_id = session.payment_intent or ''
                order.save(update_fields=['status', 'stripe_payment_intent_id'])
            return HttpResponse(f'Payment successful. Order #{order.pk}')

    return HttpResponse('Payment status unavailable.')


def checkout_cancel(request):
    return HttpResponse('Payment cancelled.')


async def async_book_list(request):
    books_queryset = Book.objects.select_related('category').order_by('title')
    books = await sync_to_async(list)(books_queryset)
    results = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'price': str(book.price),
        'category': book.category.name,
    } for book in books]
    return JsonResponse({'count': len(results), 'results': results})


async def async_book_detail(request, pk):
    try:
        book = await sync_to_async(Book.objects.select_related('category').get)(pk=pk)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found.'}, status=404)
    return JsonResponse({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'price': str(book.price),
        'stock': book.stock,
        'category': book.category.name,
    })


async def async_cart_summary(request):
    cart = await sync_to_async(lambda: request.session.get('cart', {}))()
    total = Decimal('0.00')
    for book_id, item in cart.items():
        try:
            book = await sync_to_async(Book.objects.get)(pk=book_id)
        except Book.DoesNotExist:
            continue
        total += Decimal(str(book.price)) * int(item.get('quantity', 0))
    return JsonResponse({'items': len(cart), 'total': str(total)})


class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category')
        search_query = self.request.GET.get('search', '').strip()

        if search_query:
            queryset = queryset.filter(title__icontains=search_query) | queryset.filter(author__icontains=search_query)

        return queryset.distinct().order_by('title')


class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'price', 'description', 'stock', 'category']
    template_name = 'books/book_form.html'
    permission_required = 'books.add_book'
    raise_exception = True
    success_url = reverse_lazy('books:list')


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'price', 'description', 'stock', 'category']
    template_name = 'books/book_form.html'
    permission_required = 'books.change_book'
    raise_exception = True
    success_url = reverse_lazy('books:list')


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    permission_required = 'books.delete_book'
    raise_exception = True
    success_url = reverse_lazy('books:list')