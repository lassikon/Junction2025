"""
Test script for the new SQLite-based decision history system

This script validates that:
1. Decision history utilities work correctly
2. Context formatting produces proper LLM-ready strings
3. Automatic summarization triggers when >10 decisions
"""

import asyncio
from sqlmodel import create_engine, SQLModel, Session, select
from models import PlayerProfile, GameState, DecisionHistory, EducationPath, RiskAttitude, GameStatus
from utils import (
    get_recent_decisions,
    format_decisions_for_llm,
    create_decision_summary,
    get_decision_context_for_llm
)
from database import async_engine, async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession


async def create_test_data():
    """Create test player with decision history"""
    print("Creating test data...")
    
    async with async_session_maker() as session:
        # Create test profile
        profile = PlayerProfile(
            session_id="test_session_123",
            player_name="Test Player",
            age=25,
            city="Helsinki",
            education_path=EducationPath.UNIVERSITY,
            risk_attitude=RiskAttitude.BALANCED,
            starting_savings=5000.0,
            starting_debt=10000.0
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        
        # Create game state
        game_state = GameState(
            profile_id=profile.id,
            current_step=5,
            game_status=GameStatus.ACTIVE,
            current_age=25,
            years_passed=0.5,
            money=6000.0,
            monthly_income=2500.0,
            monthly_expenses=1500.0,
            investments=3000.0,
            passive_income=50.0,
            debts=8000.0,
            fi_score=3.33,
            energy=65,
            motivation=70,
            social_life=60,
            financial_knowledge=45
        )
        session.add(game_state)
        await session.commit()
        
        # Create 12 decision history entries
        decisions_data = [
            ("paycheck", "Save 20% for emergency fund", "Started building financial security", 0.5, 1.2, 5000, 5500),
            ("unexpected_expense", "Pay with credit card", "Increased debt slightly", 1.2, 1.0, 5500, 5300),
            ("investment_opportunity", "Invest €500 in index fund", "Started long-term investment", 1.0, 1.5, 5300, 4800),
            ("paycheck", "Increase savings rate to 30%", "Accelerated emergency fund growth", 1.5, 2.0, 4800, 5300),
            ("budget_choice", "Cut entertainment budget", "Improved savings but reduced social life", 2.0, 2.3, 5300, 5600),
            ("curveball", "Car repair €800", "Used emergency fund wisely", 2.3, 2.1, 5600, 4800),
            ("paycheck", "Keep investing consistently", "Building investment habit", 2.1, 2.5, 4800, 5300),
            ("learning_opportunity", "Take online finance course", "Improved financial knowledge", 2.5, 2.8, 5300, 5200),
            ("investment_opportunity", "Invest €1000 more", "Doubled down on investing", 2.8, 3.0, 5200, 4200),
            ("paycheck", "Extra income from side gig", "Increased total income", 3.0, 3.2, 4200, 5000),
            ("debt_payment", "Pay off €2000 debt", "Reduced financial burden", 3.2, 3.3, 5000, 3500),
            ("paycheck", "Maintain investment discipline", "Steady progress towards FI", 3.3, 3.33, 3500, 4000),
        ]
        
        for i, (event_type, option, consequence, fi_before, fi_after, money_before, money_after) in enumerate(decisions_data, 1):
            decision = DecisionHistory(
                profile_id=profile.id,
                step_number=i,
                event_type=event_type,
                narrative=f"You're at age {25}, step {i}. A {event_type} event occurs.",
                options_presented=[option, "Alternative option 1", "Alternative option 2"],
                chosen_option=option,
                money_before=money_before,
                fi_score_before=fi_before,
                energy_before=70,
                motivation_before=75,
                social_before=65,
                money_after=money_after,
                fi_score_after=fi_after,
                energy_after=68,
                motivation_after=72,
                social_after=63,
                consequence_narrative=consequence,
                learning_moment="Keep building good habits!" if i % 3 == 0 else None
            )
            session.add(decision)
        
        await session.commit()
        print(f"✅ Created test profile (ID: {profile.id}) with 12 decisions")
        return profile.id


async def test_get_recent_decisions(profile_id: int):
    """Test retrieving recent decisions"""
    print("\n" + "="*80)
    print("TEST 1: Get Recent Decisions (last 5)")
    print("="*80)
    
    async with async_session_maker() as session:
        decisions = await get_recent_decisions(profile_id, session, limit=5)
        
        print(f"Retrieved {len(decisions)} decisions:")
        for d in decisions:
            print(f"  Step {d.step_number}: {d.event_type} → FI {d.fi_score_after:.2f}%")
        
        assert len(decisions) == 5, f"Expected 5, got {len(decisions)}"
        assert decisions[0].step_number < decisions[-1].step_number, "Should be chronological"
        print("✅ PASS: Retrieved decisions chronologically")


async def test_format_decisions(profile_id: int):
    """Test formatting decisions for LLM"""
    print("\n" + "="*80)
    print("TEST 2: Format Decisions for LLM Context")
    print("="*80)
    
    async with async_session_maker() as session:
        decisions = await get_recent_decisions(profile_id, session, limit=3)
        formatted = format_decisions_for_llm(decisions, include_summary=False)
        
        print("Formatted context:")
        print(formatted)
        print()
        
        assert "PLAYER'S PAST DECISIONS" in formatted
        assert "FI Score" in formatted
        assert "Money" in formatted
        print("✅ PASS: Formatted correctly for LLM")


async def test_decision_summary(profile_id: int):
    """Test AI summary generation"""
    print("\n" + "="*80)
    print("TEST 3: Create Decision Summary (>10 decisions)")
    print("="*80)
    
    async with async_session_maker() as session:
        result = await session.execute(
            select(DecisionHistory)
            .where(DecisionHistory.profile_id == profile_id)
            .order_by(DecisionHistory.step_number)
        )
        all_decisions = result.scalars().all()
        
        summary = await create_decision_summary(
            decisions=list(all_decisions),
            current_age=25,
            current_fi_score=3.33
        )
        
        print("Generated summary:")
        print(summary)
        print()
        
        assert summary is not None
        assert len(summary) > 50, "Summary should be substantial"
        print("✅ PASS: Summary generated")


async def test_full_context(profile_id: int):
    """Test the full context generation with auto-summarization"""
    print("\n" + "="*80)
    print("TEST 4: Get Full Decision Context (with auto-summary)")
    print("="*80)
    
    async with async_session_maker() as session:
        context = await get_decision_context_for_llm(
            profile_id=profile_id,
            db_session=session,
            current_age=25,
            current_fi_score=3.33,
            max_recent=3
        )
        
        print("Full context for LLM:")
        print(context)
        print()
        
        assert "JOURNEY SUMMARY" in context, "Should include summary for >10 decisions"
        assert "RECENT DECISIONS" in context
        print("✅ PASS: Full context with summary generated")


async def cleanup_test_data(profile_id: int):
    """Clean up test data"""
    print("\n" + "="*80)
    print("Cleaning up test data...")
    print("="*80)
    
    async with async_session_maker() as session:
        # Delete decisions
        await session.execute(
            select(DecisionHistory).where(DecisionHistory.profile_id == profile_id)
        )
        decisions = (await session.execute(
            select(DecisionHistory).where(DecisionHistory.profile_id == profile_id)
        )).scalars().all()
        for d in decisions:
            await session.delete(d)
        
        # Delete game state
        game_state = (await session.execute(
            select(GameState).where(GameState.profile_id == profile_id)
        )).scalar_one_or_none()
        if game_state:
            await session.delete(game_state)
        
        # Delete profile
        profile = (await session.execute(
            select(PlayerProfile).where(PlayerProfile.id == profile_id)
        )).scalar_one_or_none()
        if profile:
            await session.delete(profile)
        
        await session.commit()
        print("✅ Test data cleaned up")


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("DECISION HISTORY SYSTEM TESTS")
    print("="*80)
    
    # Create database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    profile_id = None
    try:
        # Create test data
        profile_id = await create_test_data()
        
        # Run tests
        await test_get_recent_decisions(profile_id)
        await test_format_decisions(profile_id)
        await test_decision_summary(profile_id)
        await test_full_context(profile_id)
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if profile_id:
            await cleanup_test_data(profile_id)


if __name__ == "__main__":
    asyncio.run(main())
