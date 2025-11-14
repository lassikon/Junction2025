# Database Migrations with Alembic

This project uses Alembic for database migrations to track and version control schema changes.

## Quick Start

### Create a New Migration (After Changing Models)

```bash
cd backend
alembic revision --autogenerate -m "describe your changes"
```

### Apply Migrations

```bash
cd backend
alembic upgrade head
```

### Rollback Last Migration

```bash
cd backend
alembic downgrade -1
```

## Common Commands

| Command                                    | Description                                |
| ------------------------------------------ | ------------------------------------------ |
| `alembic revision --autogenerate -m "msg"` | Auto-generate migration from model changes |
| `alembic upgrade head`                     | Apply all pending migrations               |
| `alembic downgrade -1`                     | Rollback last migration                    |
| `alembic current`                          | Show current migration version             |
| `alembic history`                          | Show migration history                     |
| `alembic upgrade +1`                       | Apply next migration                       |
| `alembic downgrade base`                   | Rollback all migrations                    |

## Makefile Commands

For convenience, use these make commands from the project root:

```bash
make migrate MSG="your migration message"  # Create new migration
make db-upgrade                            # Apply migrations
make db-downgrade                          # Rollback last migration
make db-status                            # Show current migration status
```

## Workflow

### 1. Modify Your Models

Edit `models.py` to add/modify/remove fields or tables:

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    # Add new field:
    age: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Generate Migration

```bash
cd backend
alembic revision --autogenerate -m "add age field to user"
```

This creates a new migration file in `alembic/versions/` with the changes detected.

### 3. Review Migration

Always review the generated migration file before applying it. Alembic may not detect all changes automatically (like renamed columns).

### 4. Apply Migration

```bash
alembic upgrade head
```

### 5. Commit to Git

```bash
git add alembic/versions/
git commit -m "Add age field to user model"
```

## Best Practices

1. **Always review auto-generated migrations** - Alembic might miss some changes
2. **Test migrations on development database first** - Never apply untested migrations to production
3. **Write descriptive migration messages** - Makes it easier to understand history
4. **One logical change per migration** - Easier to rollback if needed
5. **Commit migrations to version control** - Essential for team collaboration
6. **Never edit applied migrations** - Create a new migration instead
7. **Include both upgrade and downgrade** - Ensure you can rollback if needed

## Troubleshooting

### Migration conflicts

If you have migration conflicts (multiple branches creating migrations):

```bash
alembic merge <rev1> <rev2> -m "merge migrations"
```

### Reset migrations (DANGER - loses data)

```bash
# Delete database
rm app.db

# Remove all migration files except __init__.py
rm alembic/versions/*.py

# Create fresh initial migration
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

### Manual migration

If autogenerate doesn't detect your changes:

```bash
alembic revision -m "manual changes"
# Edit the generated file manually
alembic upgrade head
```

## Adding New Models

When you add a new model:

1. Import it in `alembic/env.py`:

   ```python
   from models import User, ChatHistory, YourNewModel
   ```

2. Generate migration:

   ```bash
   alembic revision --autogenerate -m "add your_new_model table"
   ```

3. Apply migration:
   ```bash
   alembic upgrade head
   ```

## Docker Usage

When using Docker, run migrations inside the container:

```bash
docker-compose exec backend alembic upgrade head
```

Or add to your Dockerfile/entrypoint to run on startup.

## Production Deployment

For production, include migration in your deployment process:

```bash
# In your deployment script
cd backend
alembic upgrade head
# Then start your application
uvicorn main:app --host 0.0.0.0 --port 8000
```
