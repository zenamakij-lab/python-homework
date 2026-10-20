import csv
from datetime import datetime
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone

from .models import Book, Order


@shared_task
def send_order_email(order_id):
    order = Order.objects.select_related("user").get(pk=order_id)
    subject = f"Order #{order.pk} confirmation"
    message = (
        f"Thank you for your order #{order.pk}.\n"
        f"Email: {order.email}\n"
        f"Total: {order.total_price}\n"
        f"Status: {order.get_status_display()}"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )
    return f"Email sent to {order.email}"


@shared_task
def generate_books_report(output_path="reports/books_report.csv"):
    books = Book.objects.select_related("category").order_by("title")
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["id", "title", "author", "price", "stock", "category"])
        for book in books:
            writer.writerow(
                [
                    book.pk,
                    book.title,
                    book.author,
                    str(book.price),
                    book.stock,
                    book.category.name,
                ]
            )

    return str(destination)


@shared_task
def cleanup_expired_sessions():
    deleted, _ = Session.objects.filter(expire_date__lt=timezone.now()).delete()
    cache.clear()
    return deleted


@shared_task
def generate_books_report_periodic():
    report_path = (
        Path(settings.BASE_DIR)
        / "reports"
        / f'books_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )
    return generate_books_report(str(report_path))
