# Recipe API

A FastAPI-based backend for creating, updating, deleting and searching recipes.
The project uses a **layered architecture (controller → service → repository → domain)** with PostgreSQL, SQLAlchemy, 
and Docker.

---

# Tech Stack

* **FastAPI** (web framework)
* **SQLAlchemy** (ORM)
* **PostgreSQL 16** (database)
* **Alembic** (migrations)
* **Docker + Docker Compose**
* **Pytest** (testing)
* **JWT Authentication (OAuth2 password flow)**

---

# Architecture Overview

This project follows a **layered architecture**:

```
app/
├── controller/        → API routes (FastAPI routers)
├── service/          → Business logic layer
├── repository/       → Database access layer
├── domain/
│   ├── model/        → SQLAlchemy models
│   └── schema/       → Pydantic DTOs
├── core/
│   ├── auth.py       → Authentication logic (JWT, user auth)
│   ├── database.py   → DB session + Base
│   ├── services.py   → Service container
│   └── service_factory.py
├── scripts/          → Setup + seeding scripts
```

### Flow

```
Request → Controller → Service → Repository → Database
```

Authentication is handled via:

* JWT tokens (`/auth/login`)
* Dependency injection (`get_current_user`)

---


---

# Database Design

### Main tables:

* `user` → user profile
* `account` → authentication credentials
* `recipe`
* `ingredient`
* `recipe_ingredient` (many-to-many)
* `recipe_step`

### Key relationships:

* User ↔ Account (1:1)
* Recipe ↔ Ingredients (M:N)
* Recipe ↔ Steps (1:M)

for more information about the database architecture, see [Database Architecture](app/domain/ReadMe.md)

---

---

# Authentication & Authorization

All write operations (`POST`, `PUT`, `DELETE`) require JWT authentication.

### Rationale

* Ensures only authenticated users can modify data
* Demonstrates awareness of **production security practices**
* Adds a basic accountability layer (actions tied to a user)
* Acts as a deterrent against misuse (non-anonymous actions)

### Current limitation

* No ownership-based authorization
* Any authenticated user can modify any recipe

### Intended improvement

* Link recipes to users (`recipe.user_id`)
* Enforce ownership in service layer
* Add role-based access (e.g. admin overrides)

### Note on traceability

Authentication lays the groundwork for **auditability**:

* Actions can be traced back to users
* Enables logging and monitoring of suspicious behavior
* Important for handling unexpected or malicious data changes


# Running the Project

## Option 1: Run with Docker (Recommended)

### 1. Create `.env` file (IMPORTANT)

Rename `.env.example` to `.env` or create a `.env` file in the project root:

```env
DB_NAME=${postgres_db}
DB_USER=${postgres_user}
DB_PASSWORD=${prostgres_pasword}
DB_HOST=db
DB_PORT=5432

SECRET_AUTH_KEY=your_generated_secret
```

Generate a secure JWT secret:

```bash
openssl rand -hex 32
```

> `SECRET_AUTH_KEY` is used to sign JWT tokens and must be kept secret.

Set the database name, username and password and secret auth key. 
Note that `DB_HOST` needs to be set to exactly db and `DB_PORT` needs to be set to exactly 5432.

```env
DB_USER=recipemaster
DB_PASSWORD=strongPassword123
DB_NAME=recipebank
```

---

### 2. Start everything

```bash
docker compose up --build
```

This will start:

* PostgreSQL (`db`)
* FastAPI API (`api`)

---

### 3. API will be available at:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## Option 2: Run locally (without Docker)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Start PostgreSQL locally

Make sure you have a PostgreSQL instance running.

Create a database and a password-protected user with sufficient privileges:

* The user should own the database **or** have full privileges
* The user must be able to **create tables, read, and write data**

Example:

```sql
CREATE DATABASE recipebank;
CREATE USER recipemaster WITH PASSWORD 'strongPassword123';
ALTER DATABASE recipebank OWNER TO recipemaster;
```

---

### 3. Configure environment variables

Rename `.env.example` to `.env` or create a `.env` file in the project root:

```env
DB_NAME=${postgres_db}
DB_USER=${postgres_user}
DB_PASSWORD=${prostgres_pasword}
DB_HOST=${postgres_host_ip}
DB_PORT=${prostgres_port}

SECRET_AUTH_KEY=your_generated_secret
```

Generate a secure JWT secret:

```bash
openssl rand -hex 32
```

> `SECRET_AUTH_KEY` is used to sign JWT tokens and must be kept secret.

Set the environment variables in `.env` to the setup of the database created in step 2. 

---

### 4. Run migrations

```bash
alembic upgrade head
```

---

### 5. Run setup script

This initializes the database schema and seeds it:

```bash
python -m app.scripts.set_up
```

---

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

---

# Authentication

## Create user

```http
POST /auth/create
```

Example body:

```json
{
  "username": "jan",
  "email": "jan@email.com",
  "name": "Jan",
  "password": "secretPassword"
}
```

---

## Login

```http
POST /auth/login
```

Form data (OAuth2):

```
username=jan
password=secret
```

Response:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

---

## Auth required endpoints

Use:

```
Authorization: Bearer <token>
```

Protected routes:

* `POST /recipe/`
* `PUT /recipe/{id}`
* `DELETE /recipe/{id}`

---

# Recipe Endpoints

## Get all recipes

```http
GET /recipe/
```

---

## Create recipe (auth required)

```http
POST /recipe/
```

---

## Get recipe by id

```http
GET /recipe/{recipe_id}
```

---

## Update recipe (auth required)

```http
PUT /recipe/{recipe_id}
```

---

## Delete recipe (auth required)

```http
DELETE /recipe/{recipe_id}
```

---

## Query recipes

```http
POST /recipe/query
```

---

# Running Tests

## Run all tests

```bash
pytest
```

---

## Run unit tests only

```bash
pytest test/unit_tests
```

---

## Run integration tests only

```bash
pytest test/integration
```

---

## Run with verbose output

```bash
pytest -v
```

---

## Run specific test file

```bash
pytest test/integration/recipes_it.py
```

---

# Database + Migrations

## Run migrations

```bash
alembic upgrade head
```

## Create migration

```bash
alembic revision --autogenerate -m "message"
```

---

---

# 🔧 Environment Variables

| Variable         | Description                  |
|------------------|------------------------------|
| DB_USER          | Postgres user                |
| DB_PASSWORD      | Postgres password            |
| DB_NAME          | Database name                |
| DATABASE_URL     | SQLAlchemy connection string |
| SECRET_AUT_TOKEN | Used for jwt generation      |

---

---

# Suggested Improvements

* Add keycloak
* Add Redis caching
* Add Search through ElasticSearch
* Add refresh tokens
* Add role-based access (admin/user)
* Add pagination to recipe endpoints
* Add OpenTelemetry logging
* Move secrets to Docker secrets / Vault
* Add CI pipeline

---
