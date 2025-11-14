#!/bin/bash
# Initialize Alembic migrations for the first time

echo "🚀 Initializing Alembic migrations..."
echo ""

cd "$(dirname "$0")"

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo "❌ Alembic is not installed. Installing from requirements.txt..."
    pip install -r requirements.txt
fi

# Check if migrations already exist
if [ -d "alembic/versions" ] && [ "$(ls -A alembic/versions)" ]; then
    echo "⚠️  Warning: Migration files already exist in alembic/versions/"
    read -p "Do you want to create a new migration anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Backup existing database if it exists
if [ -f "app.db" ]; then
    echo "📦 Backing up existing database..."
    cp app.db app.db.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created"
fi

# Create initial migration
echo "📝 Creating initial migration..."
alembic revision --autogenerate -m "initial migration"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Initial migration created successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Review the migration file in alembic/versions/"
    echo "2. Run: alembic upgrade head (or make db-upgrade)"
    echo "3. Commit the migration files to git"
    echo ""
    echo "📚 For more information, see: MIGRATIONS_README.md"
else
    echo ""
    echo "❌ Failed to create migration. Please check the errors above."
    exit 1
fi
