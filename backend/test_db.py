"""
Quick test script to verify database setup and basic operations.
Run this to ensure everything is working correctly.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import init_db, close_db, get_async_session
from models import (
    PlayerProfile, GameState, DecisionHistory,
    EducationPath, RiskAttitude, GameStatus
)
from utils import (
    initialize_game_state,
    generate_session_id,
    calculate_fi_score,
    calculate_balance_score
)


async def test_database_operations():
    """Test basic database operations"""
    print("🧪 Testing LifeSim Database...")
    print()

    # Initialize database
    print("1. Initializing database...")
    await init_db()
    print("   ✅ Database initialized")
    print()

    # Test creating a player profile
    print("2. Creating test player profile...")
    session_id = generate_session_id()

    test_profile = PlayerProfile(
        session_id=session_id,
        age=22,
        city="Helsinki",
        education_path=EducationPath.UNIVERSITY,
        risk_attitude=RiskAttitude.BALANCED,
        starting_savings=2000.0,
        starting_debt=0.0,
        aspirations={"own_car": True, "travel": True}
    )

    async with get_async_session() as session:
        session.add(test_profile)
        await session.flush()
        profile_id = test_profile.id

        print(f"   ✅ Profile created with ID: {profile_id}")
        print(f"   Session ID: {session_id}")
        print()

        # Initialize game state
        print("3. Initializing game state...")
        initial_state = initialize_game_state(test_profile)
        game_state = GameState(
            profile_id=profile_id,
            **initial_state
        )

        # Calculate FI score
        game_state.fi_score = calculate_fi_score(
            game_state.passive_income,
            game_state.monthly_expenses
        )

        session.add(game_state)
        await session.commit()
        await session.refresh(game_state)

        print(f"   ✅ Game state initialized")
        print(f"   Money: €{game_state.money}")
        print(f"   Monthly Income: €{game_state.monthly_income}")
        print(f"   Monthly Expenses: €{game_state.monthly_expenses}")
        print(f"   FI Score: {game_state.fi_score}%")
        print(f"   Energy: {game_state.energy}/100")
        print(f"   Motivation: {game_state.motivation}/100")
        print(f"   Social Life: {game_state.social_life}/100")
        print()

        # Calculate balance score
        balance = calculate_balance_score(
            game_state.energy,
            game_state.motivation,
            game_state.social_life
        )
        print(f"   Balance Score: {balance:.1f}/100")
        print()

        # Test querying
        print("4. Testing database queries...")
        result = await session.execute(
            select(PlayerProfile).where(PlayerProfile.session_id == session_id)
        )
        found_profile = result.scalar_one_or_none()

        if found_profile:
            print(f"   ✅ Successfully queried profile")
            print(f"   Age: {found_profile.age}")
            print(f"   City: {found_profile.city}")
            print(f"   Education: {found_profile.education_path}")
            print(f"   Risk Attitude: {found_profile.risk_attitude}")
        print()

        # Test updating game state
        print("5. Testing game state updates...")
        game_state.money += 500
        game_state.investments = 1000
        game_state.passive_income = 5
        game_state.fi_score = calculate_fi_score(
            game_state.passive_income,
            game_state.monthly_expenses
        )
        game_state.current_step = 1

        await session.commit()
        await session.refresh(game_state)

        print(f"   ✅ Game state updated")
        print(f"   New Money: €{game_state.money}")
        print(f"   Investments: €{game_state.investments}")
        print(f"   New FI Score: {game_state.fi_score}%")
        print(f"   Current Step: {game_state.current_step}")
        print()

        # Test decision history
        print("6. Creating decision history...")
        decision = DecisionHistory(
            profile_id=profile_id,
            step_number=1,
            event_type="first_paycheck",
            narrative="You received your first paycheck! What will you do?",
            options_presented=[
                "Save 50% for emergency fund",
                "Invest in index funds",
                "Spend on celebration with friends"
            ],
            chosen_option="Save 50% for emergency fund",
            money_before=2000,
            money_after=2500,
            fi_score_before=0,
            fi_score_after=0.42,
            energy_before=70,
            energy_after=70,
            motivation_before=70,
            motivation_after=75,
            social_before=70,
            social_after=65,
            consequence_narrative="Good choice! You now have €2,500 in savings. Building an emergency fund is a smart first step.",
            learning_moment="Financial experts recommend saving 3-6 months of expenses as an emergency fund."
        )

        session.add(decision)
        await session.commit()

        print("   ✅ Decision history saved")
        print()

        # Query all decisions for this profile
        print("7. Querying decision history...")
        result = await session.execute(
            select(DecisionHistory)
            .where(DecisionHistory.profile_id == profile_id)
            .order_by(DecisionHistory.step_number)
        )
        decisions = result.scalars().all()

        print(f"   ✅ Found {len(decisions)} decision(s)")
        for d in decisions:
            print(f"   Step {d.step_number}: {d.event_type}")
            print(f"   Chosen: {d.chosen_option}")
        print()

    # Close database
    print("8. Closing database...")
    await close_db()
    print("   ✅ Database closed")
    print()

    print("🎉 All tests passed successfully!")
    print()
    print("Next steps:")
    print("- Start the FastAPI server: uvicorn main:app --reload")
    print("- Test the API endpoints: /api/onboarding, /api/game/{session_id}")
    print("- Implement the /api/step endpoint for game progression")


if __name__ == "__main__":
    asyncio.run(test_database_operations())
