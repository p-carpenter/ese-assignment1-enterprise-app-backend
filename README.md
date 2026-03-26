# Enterprise Audio Application Backend

A robust, secure, and scalable RESTful API built with Django 6 and Django REST Framework (DRF). This backend serves as the core data layer for the Enterprise Audio Application, handling complex relational data, secure authentication, and high-concurrency playlist management.

## Features

## 🔐 Secure Authentication & Authorisation

- **HTTP-Only JWTs**: Authentication uses JSON Web Tokens stored securely in HTTP-only cookies via `dj-rest-auth`, mitigating XSS attack vectors.
    
- **Complete Auth Flow**: Full support for registration, mandatory email verification (via SendGrid), login, and password resets (via SendGrid).
    
- **Granular Permissions**: Custom permission classes (`IsOwnerOrReadOnly`, `IsOwnerOrCollaborator`) ensure users can only modify their own content or collaborative playlists.
    

## 🗂️ Advanced Content Management

- **Concurrency-Safe Playlists**: Adding songs to playlists uses database-level locking (`select_for_update`) to prevent race conditions when calculating track order.
    
- **Collaborative Playlists**: Support for public and collaborative playlists where multiple users can contribute simultaneously.
    
- **Play Tracking**: Dedicated, rate-limited endpoints for logging user listening history.
    

## 🛡️ Security & API Reliability

- **Scoped Rate Limiting**: Intelligent throttling protects critical endpoints (5 requests/minute for play logs, 10/hour for song uploads) to prevent abuse and spam.
    
- **Automated API Documentation**: OpenAPI schema generation provided out-of-the-box via `drf-spectacular`.
    
- **CORS Configuration**: Strictly configured cross-origin resource sharing to only allow requests from the authenticated frontend application.
    

## Technology Stack

- **Core Framework**: Python 3.14, Django 6.0, Django REST Framework (DRF)
    
- **Authentication**: dj-rest-auth, django-allauth, djangorestframework-simplejwt
    
- **Database**: SQLite (Development) / PostgreSQL (Production ready via `psycopg` and `dj-database-url`)
    
- **Email Delivery**: django-anymail (SendGrid)
    
- **Code Quality**: Ruff (Linting & Formatting), Coverage
    
- **Package Management**: uv (via `pyproject.toml` and `uv.lock`)
    

## Installation & Setup

## Prerequisites

- Python 3.14+
    
- `uv` (recommended for dependency management) or `pip`
    
- PostgreSQL (optional, for production parity)
    

## Setup Instructions

1. **Clone the repository**
    
    Bash
    
    ```
    git clone <repository-url>
    cd ese-assignment1-enterprise-app-backend
    ```
    
2. **Set up the environment & install dependencies** Using `uv`:
    
    Bash
    
    ```
    uv sync
    source .venv/bin/activate
    ```
    
    _Alternatively, using standard pip:_
    
    Bash
    
    ```
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```
    
3. **Configure Environment Variables** Create a `.env` file in the root directory based on your local setup:
    
    Code snippet
    
    ```
    SECRET_KEY=your_super_secret_django_key
    DEBUG=True
    RENDER_FRONTEND_URL=http://localhost:5173
    SENDGRID_API_KEY=your_sendgrid_key_here
    # DATABASE_URL=postgres://user:pass@localhost:5432/dbname # Uncomment for Postgres
    ```
    
4. **Initialise the Database**
    
    Bash
    
    ```
    python manage.py migrate
    ```
    
5. **Run the Development Server**
    
    Bash
    
    ```
    python manage.py runserver
    ```
    
    The API will be available at `http://127.0.0.1:8000`.
    

## Architecture and Layering

The application moves beyond basic Django CRUD by implementing a **Service Layer Architecture** to handle complex business logic separately from HTTP request/response handling.

## Directory Structure

Plaintext

```
backend/
├── musicplayer/            # Main application logic
│   ├── admin.py            # Django admin configurations
│   ├── models.py           # Database schemas (Song, Playlist, PlayLog)
│   ├── permissions.py      # Custom DRF permission classes
│   ├── serialisers.py      # Data validation and object serialisation
│   ├── services.py         # Isolated business logic and DB transactions
│   ├── urls.py             # App-specific routing
│   └── views.py            # DRF ViewSets and request orchestration
├── musicplayer_project/    # Core project settings and configurations
│   ├── settings.py         # Environment, Auth, and Throttling config
│   └── urls.py             # Root URL routing
├── users/                  # Custom User model and auth extensions
├── pyproject.toml          # Modern Python dependency definition
└── ruff.toml               # Linter and formatter configuration
```

## Key Technical Decisions

## 1. Service Layer for Complex Transactions (`services.py`)

Rather than placing complex database logic inside DRF ViewSets or overriding model `save()` methods, critical operations are abstracted into `services.py`.

- **Example**: `add_song_to_playlist` uses `@transaction.atomic` and `Playlist.objects.select_for_update()`. This explicit row-level database lock ensures that if multiple users add a song to a collaborative playlist at the exact same millisecond, the application will not assign them the same `order` index.

## 2. JWTs via HTTP-Only Cookies

To maximise security against Cross-Site Scripting (XSS) attacks, the application uses `dj-rest-auth` configured to issue JWTs as HTTP-Only, Secure, SameSite=None cookies (`JWT_AUTH_COOKIE` and `JWT_AUTH_REFRESH_COOKIE`). The frontend never has direct JavaScript access to the access tokens.

## 3. Decoupled Email Workflows

Because this is a headless API interacting with a SPA frontend, password resets and email verification links sent to users cannot point directly back to standard Django templates.

- **Solution**: The backend implements custom `RedirectView` classes (`PasswordResetConfirmRedirectView` and `EmailVerificationRedirectView`). The email links point to the API, which instantly parses the tokens and issues a 302 Redirect to the correct frontend React Router path, maintaining a seamless user experience.

## 4. Granular Request Throttling

To prevent abuse, the API relies on DRF's `ScopedRateThrottle`. While browsing is given a generous allowance (10000/day for authenticated users), specific actions have strict custom scopes defined in `settings.py`:

- `playlog_spam`: 20 per minute (prevents bots from artificially inflating play counts while allowing users to skip through songs quickly).
    
- `add_to_library`: 60 per minute (mitigates storage abuse and network request overload, while understanding users may add multiple songs quickly via the Jamendo API).