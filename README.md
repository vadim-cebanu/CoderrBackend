# Coderr Backend

Django project with Django REST Framework powering the Coderr platform.


## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

Follow these steps to set up the project locally:

### 1. Create Virtual Environment

Linux/Mac:
```bash
python3 -m venv venv
```

Windows:
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

Linux/Mac:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and update it with your settings:

```bash
cp .env.example .env
```

Edit `.env` and update the following variables:
- `SECRET_KEY` - Django secret key (generate a new one for production)
- `DEBUG` - Set to `True` for development, `False` for production
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

To generate a new secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)

To access the Django admin panel:

```bash
python manage.py createsuperuser
```

## Running the Application

Start the development server:

```bash
python manage.py runserver
```
## API Endpoints

- Admin: http://127.0.0.1:8000/admin/

Auth & Profiles (`auth_app`):
- `POST /api/registration/` - Register a new user
- `POST /api/login/` - Log in and obtain an auth token
- `GET/PUT/PATCH /api/profile/<pk>/` - Retrieve or update a profile
- `GET /api/profiles/business/` - List business profiles
- `GET /api/profiles/customer/` - List customer profiles

Offers (`offers_app`):
- `GET/POST /api/offers/` - List or create offers
- `GET/PUT/PATCH/DELETE /api/offers/<pk>/` - Retrieve, update, or delete an offer
- `GET /api/offerdetails/<pk>/` - Retrieve a single offer detail tier

Orders (`orders_app`):
- `GET/POST /api/orders/` - List or create orders
- `GET/PUT/PATCH/DELETE /api/orders/<pk>/` - Retrieve, update, or delete an order
- `GET /api/order-count/<business_user_id>/` - Count in-progress orders for a business user
- `GET /api/completed-order-count/<business_user_id>/` - Count completed orders for a business user

Reviews (`reviews_app`):
- `GET/POST /api/reviews/` - List or create reviews
- `GET/PUT/PATCH/DELETE /api/reviews/<pk>/` - Retrieve, update, or delete a review
- `GET /api/base-info/` - Platform-wide statistics (review count, average rating, business profile count, offer count)

## Testing

The project uses `pytest` with `pytest-django`. Settings for the test run are defined in `core/test_settings` and configured via `pytest.ini`.

Run the full test suite:

```bash
pytest
```

Run a specific test file:

```bash
pytest tests/test_offers.py
```

Run with verbose output:

```bash
pytest -v
```

Test files (in `tests/`):
- `test_auth.py` - Registration, login, and authentication
- `test_profiles.py` - Business and customer profiles
- `test_offers.py` - Offers and offer details
- `test_orders.py` - Orders, order counts, and completed order counts
- `test_reviews.py` - Reviews
- `test_base_info.py` - Platform-wide statistics endpoint
- `test_permissions.py` - Permission and access control checks

## Structure

- `core/` - Main project settings and root URL configuration
- `auth_app/` - User registration, login, and profiles
- `offers_app/` - Offers and offer details
- `orders_app/` - Orders
- `reviews_app/` - Reviews and platform statistics
- `tests/` - Test suite
- `venv/` - Virtual environment
- `.env` - Environment variables (SECRET_KEY, DEBUG, etc.)
- `.env.example` - Template for environment variables
- `manage.py` - Django management script

## Environment Variables

The project uses python-dotenv to load environment variables from `.env` file:
- `SECRET_KEY` - Django secret key (auto-generated)
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

Add more variables as needed for your project.
