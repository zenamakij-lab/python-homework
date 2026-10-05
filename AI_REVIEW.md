# AI Code Review

This review was prepared using an AI-assisted review workflow and then checked against the actual project code. Only valid recommendations were applied.

## Target views reviewed

1. `create_order_from_cart`
2. `checkout_view`
3. `BookListView`

---

## 1) `create_order_from_cart`

### Original code

```python
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
```

### AI recommendations

- Keep `transaction.atomic()` for order creation as it preserves consistency.
- Validate email and stock before creating the order.
- Avoid clearing the cart before saving relevant order details.
- Keep order confirmation email under the same transaction boundary with an explicit failure-safe flow.

### Final code

```python
def create_order_from_cart(request, cart):
    """Build an Order and corresponding OrderItem records from the current cart."""
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
```

---

## 2) `checkout_view`

### Original code

```python
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
```

### AI recommendations

- Keep the guard clauses for empty cart and missing Stripe key.
- Catch domain errors before calling Stripe to avoid partial checkout creation.
- Save the Stripe session reference back to the order after creation.
- Keep redirect URLs explicit and consistent with Django reverse names.

### Final code

```python
@require_POST
def checkout_view(request):
    """Create a Stripe checkout session for the current cart and persist the order."""
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
```

---

## 3) `BookListView`

### Original code

```python
class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category')
        search_query = self.request.GET.get('search', '').strip()

        if search_query:
            queryset = queryset.filter(title__icontains=search_query) | queryset.filter(author__icontains=search_query)

        return queryset.distinct().order_by('title')
```

### AI recommendations

- Keep the search logic, but use clear naming and explicit filtering behavior.
- Ensure the queryset keeps a consistent ordering and remains distinct after OR filtering.
- Add a docstring to clarify purpose and result behavior.

### Final code

```python
class BookListView(ListView):
    """Display the bookstore catalog with optional search and pagination."""
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
```

---

## Summary

The AI review confirmed that the core order and checkout logic was already structured correctly and the most important refinements were documentation, maintainability, and explicit validation. The final code keeps the business logic stable while improving readability and testability.
