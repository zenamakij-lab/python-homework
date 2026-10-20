import logging
from decimal import Decimal

import requests
from django.conf import settings

logger = logging.getLogger("books.api")


def sync_order_to_warehouse(order):
    if not getattr(settings, "PROJECT_B_API_URL", ""):
        logger.info("ProjectB API URL not configured; skipping warehouse sync for order #%s", order.pk)
        return None

    payloads = []
    for item in order.items.select_related("book").all():
        payloads.append(
            {
                "sku": f"BOOK-{item.book_id}",
                "quantity": int(item.quantity),
                "action": "reserve",
                "order_id": f"ORDER-{order.pk}",
            }
        )

    for payload in payloads:
        try:
            response = requests.post(
                f"{settings.PROJECT_B_API_URL}/api/warehouse/sync/",
                json=payload,
                timeout=5,
            )
            response.raise_for_status()
            logger.info(
                "Warehouse reservation synced for order #%s sku=%s status=%s",
                order.pk,
                payload["sku"],
                response.status_code,
            )
        except requests.RequestException as exc:
            logger.exception(
                "Warehouse sync failed for order #%s sku=%s: %s",
                order.pk,
                payload["sku"],
                exc,
            )
            raise RuntimeError(f"Warehouse sync failed for order #{order.pk}: {exc}")

    return True
