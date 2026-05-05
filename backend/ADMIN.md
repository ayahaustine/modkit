# ModKit Admin Guide

The admin panel is powered by [starlette-admin](https://jowilf.github.io/starlette-admin/) and mounted at `/admin`.
Access is restricted to users with `is_superuser=True`.

---

## Creating a superuser

```bash
# Docker
make create-superuser

# Local (no Docker)
cd backend && uv run python scripts/create_superuser.py
```

To promote an existing account, run the script with the same email — it will update the record in place.

---

## Adding a new model to the admin

### 1. Define the ORM model

Create `backend/modules/<your_module>/models.py`

Example:

```python
import uuid
from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, TimestampMixin

class Product(Base, TimestampMixin):
    """A sellable product."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=False), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_cents: Mapped[int]
```

### 2. Register the model with Alembic

Add an import to `backend/db/models.py`:

```python
from modules.your_module.models import Product  # noqa: F401
```

Then generate and apply the migration:

```bash
make migrate-create msg="add products table"
make migrate
```

### 3. Create the admin view

Add a class to `backend/admin/views.py`:

```python
from modules.your_module.models import Product

class ProductAdmin(ModelView):
    """Admin view for products."""

    fields = ["id", "name", "price_cents", "created_at", "updated_at"]
    exclude_fields_from_create = ["id", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]
    searchable_fields = ["name"]
    sortable_fields = ["name", "price_cents", "created_at"]


def make_product_admin() -> ProductAdmin:
    """Instantiate ProductAdmin bound to the Product model."""
    return ProductAdmin(Product, label="Products", icon="fa fa-box")
```

### 4. Register the view in the factory

In `backend/admin/__init__.py`, import and add the view:

```python
from admin.views import make_product_admin   # add to existing imports

def create_admin() -> Admin:
    ...
    admin.add_view(make_product_admin())     # add this line
    return admin
```

---

## Customising permissions

Override any of these methods on your `ModelView` subclass:

```python
from starlette.requests import Request

class ProductAdmin(ModelView):
    def can_create(self, request: Request) -> bool:
        return True   # allow all authenticated admins

    def can_edit(self, request: Request) -> bool:
        return True

    def can_delete(self, request: Request) -> bool:
        # Only allow delete in non-production environments
        return request.app.state.settings.APP_ENV != "production"

    def can_view_details(self, request: Request) -> bool:
        return True
```

---

## Customising the login check

`AdminAuthProvider` in `backend/admin/auth.py` currently allows any active superuser.
To restrict further (e.g. by role or IP), edit the `login` method:

```python
async def login(self, username, password, remember_me, request, response):
    # Add extra checks here before setting the session keys
    ...
```

---

## Available icon names

The `icon` parameter on each view accepts any [Font Awesome 4](https://fontawesome.com/v4/icons/) class string, e.g.:

| Value | Icon |
|---|---|
| `fa fa-users` | Users |
| `fa fa-key` | Sessions / keys |
| `fa fa-box` | Products |
| `fa fa-file-text` | Documents |
| `fa fa-cog` | Settings |

---

## File layout

```
backend/
  admin/
    __init__.py   # create_admin() factory — register new views here
    auth.py       # AdminAuthProvider — login / session / logout logic
    views.py      # ModelView subclasses — one per domain model
  scripts/
    create_superuser.py   # interactive CLI for superuser creation
```
