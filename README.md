# Django Ecommerce API

A full-featured, modular Django REST Framework-based backend for an ecommerce platform, with JWT authentication, Stripe integration, AWS S3 static/media storage, and robust error handling.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Modules & Structure](#modules--structure)
- [Key Libraries](#key-libraries)
- [API Endpoints](#api-endpoints)
  - [Accounts](#accounts)
  - [Products](#products)
  - [Orders](#orders)
  - [Authentication](#authentication)
- [User Flow Example](#user-flow-example)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Error Handling](#error-handling)

---

## Project Overview

This project provides a backend API for an ecommerce application, supporting user registration, authentication, product management, order processing, reviews, password reset, and payment via Stripe. Static and media files are managed with AWS S3.

---

## Modules & Structure

- **product**: Product catalog, images, reviews, filtering.
- **account**: User registration, authentication, profile, password reset.
- **order**: Order creation, management, Stripe checkout, webhooks.
- **utils**: Helpers, custom error handling, global exception formatting.

---

## Key Libraries

| Library                        | Purpose                                                      |
|---------------------------------|--------------------------------------------------------------|
| Django                         | Main web framework                                           |
| djangorestframework            | REST API support                                             |
| djangorestframework_simplejwt  | JWT authentication                                           |
| drf-yasg                       | Auto-generated Swagger/OpenAPI documentation                 |
| django-filter                  | Filtering for API endpoints                                  |
| django-storages, boto3         | AWS S3 integration for static/media files                    |
| psycopg                        | PostgreSQL database driver                                   |
| stripe                         | Stripe payment integration                                   |

---

## API Endpoints

### Accounts

| Endpoint                        | Method | Description                       | Auth Required |
|----------------------------------|--------|-----------------------------------|--------------|
| `/api/register/`                | POST   | Register a new user               | No           |
| `/api/get-user/`                | GET    | Get current user info             | Yes          |
| `/api/update-user/`             | PUT    | Update user profile               | Yes          |
| `/api/forgot-password/`         | POST   | Request password reset            | No           |
| `/api/reset-password/<token>/`  | POST   | Reset password with token         | No           |

### Products

| Endpoint                                 | Method | Description                       | Auth Required |
|-------------------------------------------|--------|-----------------------------------|--------------|
| `/api/products/`                         | GET    | List products (with filters)      | No           |
| `/api/products/<id>/`                    | GET    | Get product details               | No           |
| `/api/products/create/`                  | POST   | Create product                    | Admin        |
| `/api/products/<id>/update/`             | PUT    | Update product                    | Admin/Owner  |
| `/api/products/<id>/delete/`             | DELETE | Delete product                    | Admin/Owner  |
| `/api/products/upload-images/`            | POST   | Upload images for a product       | Admin        |
| `/api/products/<id>/add-review/`         | POST   | Add or update a review            | Yes          |
| `/api/products/<id>/delete-review/`      | DELETE | Delete own review                 | Yes          |

### Orders

| Endpoint                                 | Method | Description                       | Auth Required |
|-------------------------------------------|--------|-----------------------------------|--------------|
| `/api/orders/create/`                    | POST   | Create order (manual payment)     | Yes          |
| `/api/orders/get/`                       | GET    | List user's orders                | Yes          |
| `/api/orders/<id>/`                      | GET    | Get order details                 | Yes          |
| `/api/orders/<id>/process/`              | PUT    | Update order status/payment       | Admin/Owner  |
| `/api/orders/<id>/delete/`               | DELETE | Delete order                      | Admin/Owner  |
| `/api/create-checkout-session/`          | POST   | Create Stripe checkout session    | Yes          |
| `/api/orders/webhook/`                   | POST   | Stripe webhook for payment        | No           |

### Authentication

| Endpoint                        | Method | Description                       |
|----------------------------------|--------|-----------------------------------|
| `/api/token/`                   | POST   | Obtain JWT access/refresh tokens  |
| `/api/token/refresh/`           | POST   | Refresh JWT access token          |

---

## User Flow Example

1. **Register & Login**
    - `POST /api/register/` → User registers.
    - `POST /api/token/` → User logs in, receives JWT tokens.

2. **Browse & Filter Products**
    - `GET /api/products/?category=Electronics&min_price=100` → List products.

3. **Add to Cart & Create Order**
    - `POST /api/orders/create/` or `POST /api/create-checkout-session/` (for Stripe).

4. **Payment**
    - If Stripe, complete payment via Stripe checkout.
    - Stripe webhook (`/api/orders/webhook/`) updates order status.

5. **View Orders**
    - `GET /api/orders/get/` → See order history.

6. **Review Product**
    - `POST /api/products/<id>/add-review/` → Add a review.

7. **Password Reset**
    - `POST /api/forgot-password/` → Receive reset link.
    - `POST /api/reset-password/<token>/` → Reset password.

---

## Setup & Installation

1. **Clone the repository**
2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3. **Configure environment variables**  
   Copy `.env.example` to `.env` and fill in your secrets.
4. **Apply migrations**
    ```bash
    python manage.py migrate
    ```
5. **Create superuser**
    ```bash
    python manage.py createsuperuser
    ```
6. **Run the server**
    ```bash
    python manage.py runserver
    ```

---

## Environment Variables

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`
- `STRIPE_WEBHOOK_SECRET`
- `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`

---

## API Documentation

- **Swagger UI:** `/swagger/`
- **ReDoc:** `/redoc/`

Interactive documentation is auto-generated using **drf-yasg**.

---

## Error Handling

- All API errors are returned in a consistent JSON format.
- Custom exception handler and error views for 404/500 responses.

---

## License

MIT License

---

**Happy coding!**