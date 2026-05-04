modkit/
│
├── backend/
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── repository.py
│   │   │
│   │   ├── users/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── models.py
│   │   │   └── repository.py
│   │   │
│   │   ├── billing/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   └── repository.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   └── dependencies.py
│   │
│   ├── db/
│   │   └── base.py
│   │
│   ├── main.py
│   └── alembic/
│
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/
│   ├── lib/
│   ├── middleware.ts
│   └── Dockerfile
│
├── docs/                    # Docusaurus
│   ├── docs/
│   ├── blog/
│   └── config
│
├── e2e/                     # Playwright
│   ├── tests/
│   ├── playwright.config.ts
│   └── utils/
│
├── infra/
│   ├── nginx/
│   └── postgres/
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── release.yml
│   │   └── docs.yml
│   └── dependabot.yml
│
├── docker-compose.yml
├── Makefile
└── README.md