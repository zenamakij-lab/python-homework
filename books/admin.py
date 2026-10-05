from django.contrib import admin

from .models import Book, Category, Order, OrderItem


class BookInline(admin.TabularInline):
    model = Book
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)


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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'stripe_checkout_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
