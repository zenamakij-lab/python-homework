from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Book


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