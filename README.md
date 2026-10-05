# Bookstore Project

A Django bookstore application with product catalog, cart, order creation, Stripe checkout flow, email confirmations, user authentication, and async API endpoints.

## Features

- Book catalog with search and pagination
- Session-based shopping cart
- Order creation with transactional safety
- Stripe payment integration
- Email confirmation after checkout
- User registration and login
- Admin panel support for order management
- Internationalization (Ukrainian / English)
- Async JSON endpoints for books and cart summary
- pytest + factory-boy coverage

## Stack

- Python 3.13
- Django 6.0.6
- SQLite for local development
- PostgreSQL for production/container setup
- Redis support via Docker Compose
- Stripe API integration
- pytest, pytest-django, factory-boy

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
py -m pip install -r requirements.txt
```

3. Apply migrations:

```bash
py manage.py migrate
```

4. Run the app:

```bash
py manage.py runserver
```

5. Open the app in browser:

```text
http://127.0.0.1:8000/
```

## Docker setup

Project includes a Docker Compose configuration with:

- web (Django)
- db (PostgreSQL)
- redis

To start the environment:

```bash
docker compose up --build
```

## Testing

Run the full suite:

```bash
py -m pytest -q
```

Run coverage:

```bash
py -m pytest --cov=. --cov-report=term-missing
```

Current verified status:

- 50 tests passed
- coverage 80.60%

## AI Usage

This project includes AI-assisted review, test generation, and documentation updates.

### Prompts used

1. "Review the checkout and cart flow in the Django bookstore app and suggest improvements for transaction safety, Stripe integration, and async session access."
2. "Generate pytest tests for Book, Order, and User model logic with factory-boy and realistic assertions."
3. "Add docstrings to all Django views and class-based views in the bookstore app and keep the code readable for future maintenance."
4. "Write a README section for a Django bookstore project and include AI Usage with the exact prompts used."
5. "Create an AI review document with original code, recommendations, and final code snippets for three difficult views."

## Project notes

- Local SQLite is the default for development.
- PostgreSQL settings are configured via environment variables in `.env`.
- Stripe keys and email config can be set in `.env`.

## License

This repository is intended for educational and coursework purposes.
