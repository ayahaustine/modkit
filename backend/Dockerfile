FROM python:3.12-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# uv: copy mode needed in Docker (no hardlinks across layers), put venv outside /app
# so dev bind-mounts of ./backend:/app don't shadow it
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# Copy lockfile + metadata first for layer caching
COPY pyproject.toml uv.lock .python-version ./

# Install all dependencies (skip building the project package itself)
RUN uv sync --frozen --no-install-project

# Copy application source
COPY . .

ENV PATH="/opt/venv/bin:$PATH"
# Add /app to PYTHONPATH so `import core`, `import modules` etc. resolve
ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
