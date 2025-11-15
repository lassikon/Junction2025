#!/bin/bash
# Migration script for adding expense breakdown columns

echo "🔄 Starting expense breakdown migration..."
echo ""

cd "$(dirname "$0")"

# Check if we're in Docker or local
if [ -f "/.dockerenv" ]; then
    echo "📦 Running inside Docker container"
    IN_DOCKER=true
else
    echo "💻 Running on local machine"
    IN_DOCKER=false
fi

echo ""
echo "📝 Creating migration for expense breakdown columns..."
alembic revision --autogenerate -m "add expense breakdown columns"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to create migration"
    exit 1
fi

echo ""
echo "✅ Migration created successfully!"
echo ""
echo "🚀 Applying migration to database..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration applied successfully!"
    echo ""
    echo "📊 Current database status:"
    alembic current
    echo ""
    echo "🎉 Expense breakdown columns are now ready!"
else
    echo ""
    echo "❌ Failed to apply migration"
    exit 1
fi

