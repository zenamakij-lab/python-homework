# ProjectA + ProjectB: Bookstore and Warehouse Services

This workspace contains two Django services:

- ProjectA: bookstore application with catalog, cart, checkout, authentication, Celery tasks, Redis cache, and REST API.
- ProjectB: warehouse inventory service that handles stock reservation/release and exposes an inventory API consumed by ProjectA.

## Architecture

```text
+---------------------+      HTTP/JSON      +---------------------------+
| ProjectA (Bookstore) | ------------------> | ProjectB (Warehouse)       |
| - Django 4.2+       | <------------------ | - Django 4.2+             |
| - DRF               |  inventory sync     | - DRF                     |
| - PostgreSQL        |                     | - PostgreSQL              |
| - Redis + Celery    |                     | - Redis + Celery          |
| - JWT auth          |                     | - JWT auth                |
| - NGINX + Gunicorn  |                     | - Gunicorn                |
+---------------------+                     +---------------------------+
         |                                            |
         |                                            |
         v                                            v
   Redis cache / task broker                   Inventory + reservations
```

## Project components

### ProjectA

- Book catalog, categories, cart, orders
- Custom user model with permissions and groups
- JWT authentication and DRF endpoints
- Celery scheduled tasks and background reports
- Cache and i18n support for Ukrainian and English
- Swagger schema and admin management

### ProjectB

- InventoryItem model with stock and reservation tracking
- API endpoints for inventory listing and stock synchronization
- Error handling and logging for inter-service failures
- JWT auth and Swagger docs

## Tech stack

- Django 4.2+
- DRF
- PostgreSQL
- Redis
- Celery
- Gunicorn
- NGINX
- Docker Compose
- pytest + coverage
- Sentry monitoring support

## Local setup

### 1) Install dependencies

```bash
py -m pip install -r requirements.txt
py -m pip install -r project_b/requirements.txt
```

### 2) Create environment variables

Create a `.env` file with values such as:

```env
SECRET_KEY=your-secret-key
DEBUG=True
POSTGRES_DB=bookstore
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/0
PROJECT_B_API_URL=http://127.0.0.1:8001
SENTRY_DSN=
```

### 3) Run ProjectA

```bash
py manage.py migrate
py manage.py runserver 0.0.0.0:8000
```

### 4) Run ProjectB

```bash
cd project_b
py manage.py migrate
py manage.py runserver 0.0.0.0:8001
```

### 5) Swagger documentation

- ProjectA: http://127.0.0.1:8000/api/docs/
- ProjectB: http://127.0.0.1:8001/api/docs/

## Docker Compose

The root compose file includes both services and supporting infrastructure:

```bash
docker compose up --build
```

Services included:

- `db` PostgreSQL
- `redis`
- `web` ProjectA service
- `project_b` ProjectB service
- `celery` ProjectA worker
- `celery-beat` scheduled jobs
- `nginx` reverse proxy

## CI/CD

A GitHub Actions workflow is included under `.github/workflows/ci.yml` for:

- installation of dependencies
- Django test run
- coverage threshold checks
- lint verification

## Testing

Run ProjectA tests:

```bash
py -m pytest -q
```

Run ProjectB tests:

```bash
cd project_b
py manage.py test warehouse
```

Coverage:

```bash
py -m pytest --cov=. --cov-report=term-missing
```

## Deployment notes

- Gunicorn is used for production app serving.
- NGINX is configured as a front proxy.
- Sentry is enabled via environment variables.
- Redis is used for cache, broker, and Celery result backend.

## License

This repository is intended for educational and coursework purposes.
