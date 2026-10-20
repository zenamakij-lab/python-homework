from pathlib import Path

import pytest
from django.core.cache import cache
from django.test import override_settings

from books.models import Book, Category
from books.tasks import cleanup_expired_sessions, generate_books_report


@pytest.mark.django_db
@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
def test_book_cache_invalidation_after_update():
    category = Category.objects.create(name="Fantasy", slug="fantasy")
    book = Book.objects.create(
        title="The Hobbit",
        author="J.R.R. Tolkien",
        price="12.50",
        description="Classic novel",
        stock=10,
        category=category,
    )

    cache.set(f"book_detail:{book.pk}", {"title": "stale value"})
    book.title = "The Hobbit: Revised"
    book.save()

    assert cache.get(f"book_detail:{book.pk}") is None


@pytest.mark.django_db
def test_generate_books_report_creates_csv_file(tmp_path):
    category = Category.objects.create(name="Fantasy", slug="fantasy")
    Book.objects.create(
        title="Dune",
        author="Frank Herbert",
        price="18.00",
        description="Sci-fi classic",
        stock=5,
        category=category,
    )

    output_path = tmp_path / "books_report.csv"
    result = generate_books_report(str(output_path))

    assert Path(result).exists()
    assert "Dune" in output_path.read_text(encoding="utf-8")


@pytest.mark.django_db
def test_cleanup_expired_sessions_does_not_crash():
    assert cleanup_expired_sessions() >= 0
