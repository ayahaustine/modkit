# modkit

A full-stack SaaS starter kit. FastAPI backend, Next.js frontend, Docusaurus docs — all wired up and ready to go.

If you've ever started a project and spent the first two weeks setting up auth, Docker, migrations, and a CI pipeline before writing a single line of product code, this is for you.


## What's included

**Backend**
- FastAPI with async SQLAlchemy (SQLite in dev, PostgreSQL in production)
- JWT auth with httpOnly cookies — access token + refresh token with rotation
- Alembic migrations out of the box
- Admin panel at `/admin` via starlette-admin
- Full test suite with pytest, 74% coverage on a fresh clone

**Frontend**
- Next.js 16 App Router with TypeScript and Tailwind CSS v4
- Login, register, and dashboard pages wired to the backend
- Auth state via React context, cookie-based sessions, protected routes

**Docs**
- Docusaurus 3 with a clean minimal theme
- i18n support for English, French, Spanish, and German

**Infrastructure**
- Docker Compose for dev (SQLite, hot reload) and production (PostgreSQL)
- GitHub Actions CI for backend tests and E2E tests
- Playwright E2E tests covering login, logout, refresh token cycle, and dashboard access

---

## Getting started

**Prerequisites:** Docker Desktop, Node 20, Python 3.12, `uv`

Clone the repo and start everything:

```bash
git clone https://github.com/ayahaustine/modkit
cd modkit
make up
```

Services will be available at:

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:3000      |
| Backend  | http://localhost:8000      |
| Docs     | http://localhost:3001      |
| Admin    | http://localhost:8000/admin |

To create an admin account:

```bash
make create-superuser
```


## Running locally without Docker

```bash
make install       # install all deps (backend + frontend + docs + e2e)
make dev-backend   # FastAPI on :8000 with hot reload
make dev-frontend  # Next.js on :3000
make dev-docs      # Docusaurus on :3001
```



## Other useful commands

```bash
make test          # run backend tests
make lint          # ruff check + format check
make migrate       # run Alembic migrations
make e2e           # run Playwright tests (stack must be running)
make logs          # tail all Docker logs
```



## Project layout

```
backend/     FastAPI app — auth, users, sessions, admin
frontend/    Next.js app — login, register, dashboard
docs/        Docusaurus site
e2e/         Playwright tests
infra/       nginx config (production)
```

---

Built to be forked and extended, not fought with.

Have fun building :)
