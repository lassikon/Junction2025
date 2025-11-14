"""
Test script for the /api/step endpoint and game flow.
"""

import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession

from database import init_db, close_db, get_async_session
from models import (
    PlayerProfile, GameState, OnboardingRequest,
    EducationPath, RiskAttitude
)
from utils import initialize_game_state, generate_session_id, calculate_fi_score
from game_engine import get_event_type, create_decision_options, apply_decision_effects, setup_option_effect
from ai_narrative import generate_event_narrative, generate_consequence_narrative


async def test_game_flow():
    """Test complete game flow"""
    print("🎮 Testing LifeSim Game Flow\n")

    # Initialize database
    print("1. Initializing database...")
    await init_db()
    print("   ✅ Database ready\n")

    # Create test player
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

        # Initialize game state
        initial_state = initialize_game_state(test_profile)
        game_state = GameState(
            profile_id=test_profile.id,
            **initial_state
        )
        game_state.fi_score = calculate_fi_score(
            game_state.passive_income,
            game_state.monthly_expenses
        )

        session.add(game_state)
        await session.commit()
        await session.refresh(game_state)

        print(f"   ✅ Player created")
        print(f"   Session ID: {session_id}")
        print(f"   Starting Money: €{game_state.money}")
        print(f"   Monthly Income: €{game_state.monthly_income}")
        print(f"   Monthly Expenses: €{game_state.monthly_expenses}")
        print()

        # Simulate 3 game steps
        for step in range(3):
            print(f"\n{'='*60}")
            print(f"STEP {step + 1}")
            print(f"{'='*60}\n")

            # Get event type
            event_type = get_event_type(game_state, test_profile)
            print(f"📋 Event Type: {event_type}")
            print()

            # Generate narrative
            narrative = generate_event_narrative(
                event_type=event_type,
                state=game_state,
                profile=test_profile,
                curveball=None,
                client=None  # Use fallback narratives for testing
            )
            print(f"📖 Narrative:")
            print(f"   {narrative}")
            print()

            # Get options
            options = create_decision_options(event_type, game_state, None)
            print(f"🎯 Options:")
            for idx, option in enumerate(options, 1):
                print(f"   {idx}. {option['text']}")
            print()

            # Choose first option for testing
            chosen_option = options[0]
            print(f"✓ Player chooses: {chosen_option['text']}")
            print()

            # Store state before
            money_before = game_state.money
            fi_before = game_state.fi_score
            energy_before = game_state.energy

            # Apply effects
            effect = setup_option_effect(chosen_option)
            apply_decision_effects(game_state, effect)

            # Show changes
            print(f"💰 Changes:")
            print(
                f"   Money: €{money_before:.0f} → €{game_state.money:.0f} ({game_state.money - money_before:+.0f})")
            print(
                f"   FI Score: {fi_before:.1f}% → {game_state.fi_score:.1f}% ({game_state.fi_score - fi_before:+.1f}%)")
            print(
                f"   Energy: {energy_before} → {game_state.energy} ({game_state.energy - energy_before:+d})")
            print(f"   Motivation: {game_state.motivation}/100")
            print(f"   Social: {game_state.social_life}/100")
            print(f"   Knowledge: {game_state.financial_knowledge}/100")
            print()

            # Generate consequence
            consequence = generate_consequence_narrative(
                chosen_option=chosen_option['text'],
                option_effect=chosen_option,
                state=game_state,
                profile=test_profile,
                client=None
            )
            print(f"📝 Consequence:")
            print(f"   {consequence}")
            print()

        print(f"\n{'='*60}")
        print("FINAL STATE")
        print(f"{'='*60}\n")
        print(f"💰 Money: €{game_state.money:.0f}")
        print(f"📈 Investments: €{game_state.investments:.0f}")
        print(f"💸 Debts: €{game_state.debts:.0f}")
        print(f"🎯 FI Score: {game_state.fi_score:.1f}%")
        print(f"⚡ Energy: {game_state.energy}/100")
        print(f"💪 Motivation: {game_state.motivation}/100")
        print(f"👥 Social Life: {game_state.social_life}/100")
        print(f"📚 Financial Knowledge: {game_state.financial_knowledge}/100")
        print(f"📊 Current Step: {game_state.current_step}")
        print()

    await close_db()

    print("✅ Game flow test complete!")
    print()
    print("Next steps:")
    print("- Start the server: python start_server.py")
    print("- Test the API: POST /api/onboarding")
    print("- Make decisions: POST /api/step")
    print("- Check state: GET /api/game/{session_id}")


if __name__ == "__main__":
    asyncio.run(test_game_flow())
