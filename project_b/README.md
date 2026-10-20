# ProjectB Warehouse Service

ProjectB is a Django warehouse microservice built for stock management and API-based synchronization.

## Features

- InventoryItem model with available and reserved quantities
- stock reservation/release API
- JWT-based authentication
- Swagger UI schema
- Celery support
- Redis-backed caching

## Local run

```bash
cd project_b
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
```

## API

- GET /api/warehouse/inventory/
- POST /api/warehouse/sync/
- GET /api/schema/
- GET /api/docs/
