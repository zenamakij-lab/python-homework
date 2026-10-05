from decimal import Decimal

from django.conf import settings

from .models import Book


class Cart:
    def __init__(self, request):
        self.session = request.session if hasattr(request.session, 'get') else {}
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = {}
            self.session[settings.CART_SESSION_ID] = cart
        self.cart = cart

    def add(self, book, quantity=1, override_quantity=False):
        book_id = str(book.id)
        if book_id not in self.cart:
            self.cart[book_id] = {'quantity': 0, 'price': str(book.price)}

        if override_quantity:
            self.cart[book_id]['quantity'] = quantity
        else:
            self.cart[book_id]['quantity'] += quantity

        if self.cart[book_id]['quantity'] <= 0:
            del self.cart[book_id]

        self.save()

    def remove(self, book):
        book_id = str(book.id)
        if book_id in self.cart:
            del self.cart[book_id]
            self.save()

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.cart = self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        if hasattr(self.session, 'modified'):
            self.session.modified = True

    def __iter__(self):
        book_ids = list(self.cart.keys())
        books = Book.objects.filter(id__in=[int(book_id) for book_id in book_ids])
        cart_items = self.cart.copy()

        for book in books:
            item = cart_items.get(str(book.id), {})
            item['book'] = book
            item['price'] = str(book.price)
            item['total_price'] = Decimal(item['price']) * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item.get('price', '0')) * item['quantity']
            for item in self.cart.values()
        )
