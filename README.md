# AdaStream: Enterprise Audio Application Backend

A robust, secure, and scalable RESTful API built with Django 6 and Django REST Framework (DRF). This backend serves as the core data layer for the Enterprise Audio Application, handling complex relational data, secure authentication, and high-concurrency playlist management.

---

## Features

### 🔐 Secure Authentication & Authorisation

- **HTTP-Only JWTs**  
  Authentication uses JSON Web Tokens stored securely in HTTP-only cookies via `dj-rest-auth`, mitigating XSS attack vectors.

- **Complete Auth Flow**  
  Full support for registration, mandatory email verification (via SendGrid), login, and password resets (via Sendgrid).

- **Granular Permissions**  
  Custom permission classes (`IsOwnerOrReadOnly`, `IsOwnerOrCollaborator`) ensure users can only modify their own content or collaborative playlists (to add songs).

---

### 🗂️ Advanced Content Management

- **Concurrency-Safe Playlists**  
  Adding songs to playlists uses database-level locking (`select_for_update`) to prevent race conditions when calculating track order.

- **Collaborative Playlists**  
  Support for public and collaborative playlists where multiple users can contribute simultaneously.

- **Play Tracking**  
  Dedicated, rate-limited endpoints for logging user listening history.

---

### 🛡️ Security & API Reliability

- **Scoped Rate Limiting**  
  Throttling protects critical endpoints:
  - `20 requests/minute` for play logs
  - `60 requests/minute` for library additions

- **Automated API Documentation**  
  OpenAPI schema generation and interactive Swagger UI provided via `drf-spectacular`.

- **CORS Configuration**  
  Strict cross-origin resource sharing configuration allowing requests only from the authenticated frontend application.

---

## Technology Stack

| Area | Technology |
|------|------------|
| Core Framework | Python 3.14, Django 6.0, Django REST Framework |
| Authentication | dj-rest-auth, django-allauth, djangorestframework-simplejwt |
| Database | SQLite (Development), PostgreSQL (Production via `psycopg`, `dj-database-url`) |
| Media Storage | Cloudinary (Direct frontend uploads via backend signatures) |
| Email Delivery | django-anymail (SendGrid) |
| Code Quality | Ruff (Linting & Formatting), Coverage (Testing) |
| Package Management | uv (`pyproject.toml`, `uv.lock`) |

---

## Setup & Installation

### Prerequisites

- Python 3.14+
- `uv` (recommended) or `pip`
- PostgreSQL (optional, for production parity)

---

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ese-assignment1-enterprise-app-backend
```

---

### 2. Install Dependencies

#### Using `uv`

```bash
uv sync
source .venv/bin/activate
```

#### Using `pip`

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_super_secret_django_key
DEBUG=True
RENDER_FRONTEND_URL=http://localhost:5173

SENDGRID_API_KEY=your_sendgrid_key_here

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

---

### 4. Initialise the Database

```bash
python manage.py migrate
```

---

### 5. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at:

```
http://127.0.0.1:8000
```

---

## Application Usage

### Interactive API Documentation (Swagger UI)

Navigate to:

```
http://127.0.0.1:8000/
```

You can explore endpoints, payload structures, and execute requests directly from the browser.

Raw OpenAPI schema:

```
/api/schema/
```

---

## Testing & Tooling

### Run Tests with Coverage

```bash
coverage run manage.py test
coverage report
```

### Linting & Formatting

```bash
ruff check .
ruff format .
```

---

## Architecture and Layering

The application implements a **Service Layer Architecture** to separate business logic from HTTP request handling.

---

### Directory Structure

```
backend/
├── musicplayer/
│   ├── admin.py
│   ├── models.py
│   ├── permissions.py
│   ├── serialisers.py
│   ├── services.py
│   ├── tests/
│   ├── urls.py
│   └── views.py
│
├── musicplayer_project/
│   ├── settings.py
│   └── urls.py
│
├── users/
├── pyproject.toml
└── ruff.toml
```

---

## Key Technical Decisions

### 1. Direct-to-Cloud Media Uploads

Routing large audio files through Django would consume server bandwidth and block worker threads.

**Solution:**  
The backend implements a `CloudinarySignatureView`. The API generates a SHA-1 cryptographic signature, allowing the frontend to upload files directly to Cloudinary without proxying the file through Django.

---

### 2. Service Layer for Complex Transactions (`services.py`)

Complex database operations are abstracted into a dedicated service layer instead of being embedded inside ViewSets or model methods.

Example:

- `add_song_to_playlist` uses `@transaction.atomic`
- `Playlist.objects.select_for_update()`

This row-level lock ensures that concurrent requests cannot assign duplicate track order indexes.

---

### 3. JWTs via HTTP-Only Cookies

To maximise protection against XSS attacks, authentication uses:

```
JWT_AUTH_COOKIE
JWT_AUTH_REFRESH_COOKIE
```

Cookies are configured with:

- HttpOnly
- Secure
- SameSite=None

A dedicated endpoint:

```
/api/csrf/
```

ensures state-changing requests remain protected against CSRF.

---

### 4. Decoupled Email Workflows

Because this is a headless API interacting with a SPA frontend, email verification and password reset links cannot point to traditional Django templates.

**Solution:**

Custom redirect views:

- `PasswordResetConfirmRedirectView`
- `EmailVerificationRedirectView`

These endpoints parse tokens and immediately issue a `302 redirect` to the appropriate frontend route handled by React Router.

---

### 5. Custom Pagination & Filtering

All collection endpoints use custom pagination classes:

- `SongPagination`
- `PlayLogPagination`

`django-filter` integration allows filtering and sorting via query parameters without requiring custom ORM queries for each combination.

---

### 6. Granular Request Throttling

The API uses DRF's `ScopedRateThrottle`.

Default browsing allowance:

```
10000/day per authenticated user
1000/day per unauthenticated user (register, login, password reset)
```

Custom scopes:

| Scope | Limit | Purpose |
|------|------|---------|
| playlog_spam | 20/minute | Prevent artificial play inflation |
| add_to_library | 60/minute | Prevent storage abuse |