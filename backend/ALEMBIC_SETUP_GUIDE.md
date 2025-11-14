# 🔄 Alembic Migration Setup - Complete Guide

Alembic has been configured for your project! This guide will help you get started.

## ✅ What Has Been Set Up

1. ✅ **Alembic package** added to `requirements.txt`
2. ✅ **Migration structure** created in `backend/alembic/`
3. ✅ **Configuration files** set up:
   - `alembic.ini` - Main configuration
   - `alembic/env.py` - Migration environment (configured for SQLModel)
   - `alembic/script.py.mako` - Migration template
4. ✅ **Makefile commands** added for easy migration management
5. ✅ **Documentation** created (`MIGRATIONS_README.md`)
6. ✅ **Initialization script** (`init_migrations.sh`)

## 🚀 Quick Start (First Time Setup)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Create Initial Migration

Option A - Using the script:
```bash
cd backend
./init_migrations.sh
```

Option B - Manual:
```bash
cd backend
alembic revision --autogenerate -m "initial migration"
```

### Step 3: Review the Migration

Check the generated file in `backend/alembic/versions/`. It should contain:
- `user` table with id, username, email, created_at
- `chathistory` table with id, user_id, message, response, model, created_at

### Step 4: Apply the Migration

```bash
# From backend directory
alembic upgrade head

# OR from project root
make db-upgrade
```

### Step 5: Verify

```bash
# Check current migration version
make db-status

# View migration history
make db-history
```

## 📝 Daily Usage

### When You Modify Models

1. **Edit your model** in `backend/models.py`:
   ```python
   class User(SQLModel, table=True):
       id: Optional[int] = Field(default=None, primary_key=True)
       username: str = Field(index=True, unique=True)
       email: str = Field(index=True, unique=True)
       phone: Optional[str] = None  # ← New field
       created_at: datetime = Field(default_factory=datetime.utcnow)
   ```

2. **Generate migration**:
   ```bash
   # From project root
   make migrate MSG="add phone to user"
   
   # OR from backend directory
   alembic revision --autogenerate -m "add phone to user"
   ```

3. **Review the generated migration** in `alembic/versions/`

4. **Apply migration**:
   ```bash
   make db-upgrade
   ```

5. **Test your changes** - Make sure your app works

6. **Commit to git**:
   ```bash
   git add alembic/versions/
   git add models.py
   git commit -m "Add phone field to user model"
   ```

## 🛠️ Available Commands

### From Project Root (using Makefile)

| Command | Description |
|---------|-------------|
| `make migrate MSG="description"` | Create new migration |
| `make db-upgrade` | Apply all pending migrations |
| `make db-downgrade` | Rollback last migration |
| `make db-status` | Show current version |
| `make db-history` | Show all migrations |

### From backend/ Directory (using alembic directly)

| Command | Description |
|---------|-------------|
| `alembic revision --autogenerate -m "msg"` | Create migration |
| `alembic upgrade head` | Apply all migrations |
| `alembic downgrade -1` | Rollback one migration |
| `alembic current` | Show current version |
| `alembic history` | Show migration history |
| `alembic upgrade +1` | Apply next migration only |
| `alembic downgrade base` | Rollback everything |

## 🔄 Migration Workflow Diagram

```
┌─────────────────┐
│  Edit models.py │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ make migrate MSG="..."      │
│ (Auto-generates migration)  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Review migration file       │
│ in alembic/versions/        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ make db-upgrade             │
│ (Applies changes to DB)     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Test application            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Commit migration + models   │
│ to version control          │
└─────────────────────────────┘
```

## 🐳 Docker Usage

If using Docker, run migrations inside the container:

```bash
# Apply migrations in Docker
docker-compose exec backend alembic upgrade head

# Create migration in Docker
docker-compose exec backend alembic revision --autogenerate -m "your message"
```

Or add to your `docker-compose.yml` or entrypoint script to run on startup.

## 🆘 Troubleshooting

### "No such table" error
You haven't applied migrations yet:
```bash
make db-upgrade
```

### "Target database is not up to date"
Apply pending migrations:
```bash
make db-upgrade
```

### Migration not detecting changes
1. Make sure your model is imported in `alembic/env.py`
2. Check that SQLModel table=True is set
3. Try a manual migration:
   ```bash
   alembic revision -m "manual changes"
   # Edit the file manually
   alembic upgrade head
   ```

### Want to start fresh (⚠️ DESTROYS DATA)
```bash
rm backend/app.db
rm backend/alembic/versions/*.py
cd backend
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

## 📚 Learn More

- Full documentation: `backend/MIGRATIONS_README.md`
- Alembic docs: https://alembic.sqlalchemy.org/
- SQLModel docs: https://sqlmodel.tiangolo.com/

## ✨ Benefits of Using Migrations

✅ **Version Control** - Track all database schema changes
✅ **Collaboration** - Team members get same schema through git
✅ **Rollback** - Undo changes if something goes wrong
✅ **Production Safety** - Controlled, tested schema updates
✅ **Documentation** - Migration files document schema evolution
✅ **No Data Loss** - Migrations preserve existing data

## 🎯 Next Steps

1. ✅ Install dependencies: `pip install -r backend/requirements.txt`
2. ✅ Create initial migration: `./backend/init_migrations.sh`
3. ✅ Apply migration: `make db-upgrade`
4. ✅ Test your application
5. ✅ Commit migration files to git

Happy migrating! 🚀
