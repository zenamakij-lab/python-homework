from django.contrib import admin
from .models import Book, Category


class BookInline(admin.TabularInline):
    model = Book
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BookInline]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'price',
        'stock',
        'category'
    )

    list_filter = (
        'category',
        'stock',
    )

    search_fields = (
        'title',
        'author',
        'description',
    )

    list_editable = (
        'price',
        'stock',
    )