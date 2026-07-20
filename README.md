# core

Django project with Django REST Framework automatically generated.


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
- API Root: http://127.0.0.1:8000/api/

## Structure

- `core/` - Main settings
- `api/` - Sample app with API
- `venv/` - Virtual environment
- `.env` - Environment variables (SECRET_KEY, DEBUG, etc.)
- `.env.example` - Template for environment variables
- `manage.py` - Django management script

## Development

To create a superuser:
```bash
python manage.py createsuperuser
```

## Environment Variables

The project uses python-dotenv to load environment variables from `.env` file:
- `SECRET_KEY` - Django secret key (auto-generated)
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

Add more variables as needed for your project.
