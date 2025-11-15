"""
Script to populate the leaderboard with test data
Run with: python populate_leaderboard.py
"""

import asyncio
from datetime import datetime, timedelta
from sqlmodel import select
from database import async_engine, AsyncSession
from models import LeaderboardEntry, EducationPath, Account, SessionToken
from auth_utils import hash_password
import uuid
import random

# Test data
TEST_ACCOUNTS = [
    {"username": "alex_investor", "display_name": "Alex Johnson", "age": 28},
    {"username": "sara_saver", "display_name": "Sara Williams", "age": 24},
    {"username": "mike_entrepreneur", "display_name": "Mike Chen", "age": 32},
    {"username": "emma_balanced", "display_name": "Emma Garcia", "age": 26},
    {"username": "john_risktaker", "display_name": "John Smith", "age": 29},
    {"username": "lisa_careful", "display_name": "Lisa Anderson", "age": 25},
    {"username": "david_wise", "display_name": "David Lee", "age": 30},
    {"username": "maria_smart", "display_name": "Maria Rodriguez", "age": 27},
    {"username": "tom_lucky", "display_name": "Tom Wilson", "age": 31},
    {"username": "anna_strategic", "display_name": "Anna Brown", "age": 23},
]

EDUCATION_PATHS = [
    EducationPath.UNIVERSITY,
    EducationPath.VOCATIONAL,
    EducationPath.HIGH_SCHOOL,
    EducationPath.WORKING,
]


async def create_test_accounts():
    """Create test accounts"""
    async with AsyncSession(async_engine) as session:
        for account_data in TEST_ACCOUNTS:
            # Check if account already exists
            result = await session.execute(
                select(Account).where(Account.username == account_data["username"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"Account {account_data['username']} already exists, skipping...")
                continue
            
            # Create account
            account = Account(
                username=account_data["username"],
                password_hash=hash_password("test123"),
                display_name=account_data["display_name"],
                has_completed_onboarding=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            session.add(account)
            await session.flush()
            
            print(f"✅ Created account: {account_data['username']}")
        
        await session.commit()


async def populate_leaderboard():
    """Populate leaderboard with test entries"""
    async with AsyncSession(async_engine) as session:
        # Get all test accounts
        result = await session.execute(
            select(Account).where(
                Account.username.in_([acc["username"] for acc in TEST_ACCOUNTS])
            )
        )
        accounts = result.scalars().all()
        
        if not accounts:
            print("❌ No test accounts found! Run create_test_accounts first.")
            return
        
        for i, account in enumerate(accounts):
            # Generate random scores with some variance
            base_fi_score = 85 - (i * 3) + random.uniform(-5, 5)
            fi_score = max(20, min(100, base_fi_score))
            
            balance_score = random.uniform(60, 95)
            
            # Random education path
            education = random.choice(EDUCATION_PATHS)
            
            # Calculate other metrics based on FI score
            final_money = random.uniform(50000, 500000) * (fi_score / 100)
            total_income = random.uniform(100000, 1000000)
            total_spent = total_income - final_money
            
            # Life metrics
            energy = random.randint(50, 95)
            motivation = random.randint(50, 95)
            social = random.randint(50, 95)
            knowledge = random.randint(60, 100)
            
            # Create leaderboard entry
            entry = LeaderboardEntry(
                session_id=str(uuid.uuid4()),
                account_id=account.id,
                is_test_mode=False,
                player_name=account.display_name,
                age=TEST_ACCOUNTS[i % len(TEST_ACCOUNTS)]["age"],
                education_path=education,
                final_fi_score=fi_score,
                final_money=final_money,
                final_energy=energy,
                final_motivation=motivation,
                final_social=social,
                final_knowledge=knowledge,
                balance_score=balance_score,
                steps_completed=random.randint(15, 50),
                total_income_earned=total_income,
                total_spent=total_spent,
                best_decision="Invested early in index funds" if fi_score > 70 else "Started saving consistently",
                worst_decision="Bought an expensive car" if fi_score < 60 else "Took on unnecessary debt",
                completed_at=datetime.utcnow() - timedelta(days=random.randint(0, 20))
            )
            
            session.add(entry)
            print(f"✅ Added leaderboard entry for {account.display_name} (FI Score: {fi_score:.1f})")
        
        await session.commit()
        print("\n🎉 Leaderboard populated successfully!")


async def main():
    print("🚀 Starting leaderboard population...")
    print("\n📝 Step 1: Creating test accounts...")
    await create_test_accounts()
    
    print("\n📊 Step 2: Populating leaderboard...")
    await populate_leaderboard()
    
    print("\n✨ Done! You can now view the leaderboard in the app.")


if __name__ == "__main__":
    asyncio.run(main())

