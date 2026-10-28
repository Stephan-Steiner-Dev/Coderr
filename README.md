# Coderr Backend

Coderr is a REST API for a service marketplace where business users publish offers and customers place orders and write reviews. The backend is built with Django and Django REST Framework.

## Features

- User registration and login with token authentication
- Customer and business profiles
- Offer creation, listing, filtering, sorting, and pagination
- Order management and order statistics
- Business reviews and platform statistics
- Permission checks based on user roles and resource ownership

## Tech Stack

- Python
- Django
- Django REST Framework
- Token authentication (`rest_framework.authtoken`)
- SQLite for local development

See `requirements.txt` for the exact dependency versions.

## Project Structure

```text
coderr/
├── auth_app/
├── offers_app/
├── orders_app/
├── profile_app/
├── reviews_app/
├── core/                 # Django project configuration
├── manage.py
├── requirements.txt
└── README.md
```

Each app contains an `api/` directory for its API views, serializers, routes, and permissions where applicable.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Stephan-Steiner-Dev/Coderr.git
cd coderr
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv env
.\env\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```


### 4. Configure environment variables

Create a `.env` file in the project root directory
(next to `manage.py`) and add:

```dotenv
DJANGO_SECRET_KEY=your-secret-key-here
```

Never commit your `.env` file or secret keys to Git.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```


The API is available locally at `http://127.0.0.1:8000/api/`.

## Authentication

Register a user using `POST /api/registration/` and log in using `POST /api/login/`. The API uses token authentication for protected endpoints.

Include the token in the HTTP request header:

```http
Authorization: Token YOUR_TOKEN
```

Users have either a `customer` or `business` profile. Certain actions are restricted by role or ownership. Consult the API implementation for the required request fields and exact permissions.

## API Endpoints

All paths below are relative to `http://127.0.0.1:8000`.

| Method(s) | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/registration/` | Register a user |
| POST | `/api/login/` | Log in and obtain an authentication token |
| GET, POST | `/api/offers/` | List or create offers |
| GET, PATCH, DELETE | `/api/offers/<id>/` | Retrieve, update, or delete an offer |
| GET | `/api/offerdetails/<id>/` | Retrieve an offer detail |
| GET, POST | `/api/orders/` | List or create orders |
| PATCH, DELETE | `/api/orders/<id>/` | Update or delete an order |
| GET | `/api/order-count/<business_user_id>/` | Count active orders for a business user |
| GET | `/api/completed-order-count/<business_user_id>/` | Count completed orders for a business user |
| GET, PATCH | `/api/profile/<id>/` | Retrieve or update a profile |
| GET | `/api/profiles/business/` | List business profiles |
| GET | `/api/profiles/customer/` | List customer profiles |
| GET | `/api/base-info/` | Retrieve public platform statistics |
| GET, POST | `/api/reviews/` | List or create reviews |
| PATCH, DELETE | `/api/reviews/<id>/` | Update or delete a review |

> Note: The table summarizes the implemented routes discussed during development. Confirm allowed HTTP methods against the current code before publishing.

### Offer list query parameters

`GET /api/offers/` supports:

- `creator_id` — filter by creator ID
- `min_price` — filter by minimum offer price
- `max_delivery_time` — filter by delivery time
- `search` — search offer titles and descriptions
- `ordering` — `updated_at`, `-updated_at`, `min_price`, or `-min_price`
- `page` — page number
- `page_size` — number of items per page (default: 10; maximum: 100)

### Review list query parameters

`GET /api/reviews/` supports filtering by `business_user_id` and `reviewer_id` and ordering by supported rating or update-time fields.

## Tests

Run the Django test suite:

```bash
python manage.py test
```

Check the Django configuration and migrations:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```

To measure test coverage (install `coverage` if it is not already available):

```bash
coverage erase
coverage run --source=auth_app,profile_app,offers_app,orders_app,reviews_app manage.py test
coverage report -m
```

Local test coverage is not a guarantee of passing external evaluation tests.

## Django Admin

Create an administrator account:

```bash
python manage.py createsuperuser
```

Start the server and visit `http://127.0.0.1:8000/admin/`.

## Security and Repository Hygiene

Do not commit the local database, virtual environment, secrets, or cache files. Ensure your `.gitignore` excludes at least:

```gitignore
.env
env/
.venv/
db.sqlite3
__pycache__/
*.py[cod]
.coverage
htmlcov/
.pytest_cache/
```

The development server and SQLite setup are intended for local development, not production deployment.