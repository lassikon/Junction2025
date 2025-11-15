"""
Utility functions for game mechanics and calculations.

This module contains pure functions for:
- FI Score calculation
- Metric updates
- Balance calculations
- Risk factor management
"""

from models import GameState, PlayerProfile, RiskAttitude, EducationPath
from typing import Dict, Tuple
import uuid


def calculate_fi_score(passive_income: float, monthly_expenses: float) -> float:
    """
    Calculate Financial Independence Score.

    FI Score = (Passive Income / Monthly Cost of Living) × 100%

    Args:
        passive_income: Monthly passive income from investments
        monthly_expenses: Monthly cost of living

    Returns:
        FI score as a percentage (0-100+)
    """
    if monthly_expenses <= 0:
        return 0.0

    fi_score = (passive_income / monthly_expenses) * 100
    return min(fi_score, 100.0)  # Cap at 100%


def calculate_balance_score(energy: int, motivation: int, social_life: int) -> float:
    """
    Calculate overall life balance score as average of life metrics.

    Args:
        energy: Energy level (0-100)
        motivation: Motivation level (0-100)
        social_life: Social life level (0-100)

    Returns:
        Average balance score (0-100)
    """
    return (energy + motivation + social_life) / 3.0


def calculate_net_worth(
    money: float,
    investments: float,
    debts: float,
    assets_value: float = 0.0
) -> float:
    """
    Calculate total net worth.

    Net Worth = Cash + Investments + Asset Value - Debts

    Args:
        money: Current cash/savings
        investments: Value of investment portfolio
        debts: Total debt amount
        assets_value: Total value of physical assets (car, etc.)

    Returns:
        Net worth
    """
    return money + investments + assets_value - debts


def get_starting_income(education_path: EducationPath, age: int) -> float:
    """
    Determine starting monthly income based on education path and age.

    Args:
        education_path: Player's education path
        age: Player's age

    Returns:
        Starting monthly income in euros
    """
    # Base income by education path
    base_income = {
        EducationPath.VOCATIONAL: 2200,
        EducationPath.HIGH_SCHOOL: 1800,
        EducationPath.UNIVERSITY: 2500,
        EducationPath.WORKING: 2400
    }

    income = base_income.get(education_path, 2000)

    # Adjust for age (more experience = higher income)
    if age >= 25:
        income *= 1.15
    elif age >= 22:
        income *= 1.08

    return round(income, 2)


def get_starting_expenses(city: str, has_car: bool = False, has_pet: bool = False) -> float:
    """
    Calculate starting monthly expenses based on location and circumstances.

    Args:
        city: City of residence (affects rent)
        has_car: Whether player has a car
        has_pet: Whether player has a pet

    Returns:
        Monthly expenses in euros
    """
    # Base expenses by city (rent + utilities + food)
    city_costs = {
        "Helsinki": 1200,
        "Espoo": 1100,
        "Tampere": 900,
        "Turku": 850,
        "Oulu": 800,
        "Lahti": 750,
        "Kuopio": 750,
        "Jyväskylä": 800,
    }

    expenses = city_costs.get(city, 900)

    # Additional costs
    if has_car:
        expenses += 200  # Insurance, maintenance, fuel
    if has_pet:
        expenses += 50  # Food and basic care

    return round(expenses, 2)


def initialize_game_state(profile: PlayerProfile, monthly_income: float, monthly_expenses: float) -> Dict:
    """
    Initialize a new game state based on player profile.

    Args:
        profile: PlayerProfile from onboarding
        monthly_income: User-provided monthly income
        monthly_expenses: User-provided monthly expenses

    Returns:
        Dictionary with initial game state values
    """
    # Determine starting conditions
    has_car = profile.aspirations.get("own_car", False)
    has_pet = profile.aspirations.get("own_pet", False)

    # Use user-provided income and expenses instead of calculating them
    # monthly_income = get_starting_income(profile.education_path, profile.age)
    # monthly_expenses = get_starting_expenses(profile.city, has_car, has_pet)

    # Initial metrics based on risk attitude
    if profile.risk_attitude == RiskAttitude.RISK_AVERSE:
        energy = 75
        motivation = 65
        social_life = 70
    elif profile.risk_attitude == RiskAttitude.RISK_SEEKING:
        energy = 65
        motivation = 75
        social_life = 75
    else:  # BALANCED
        energy = 70
        motivation = 70
        social_life = 70

    # Build assets dictionary
    assets = {}
    if has_car:
        assets["car"] = {"type": "used_sedan", "value": 5000}
    if has_pet:
        assets["pet"] = {"type": "cat", "name": "Fluffy"}

    # Build risk factors
    risk_factors = {
        "has_car": has_car,
        "has_pet": has_pet,
        "has_rental": True,  # Assume starting with rental
        "has_loan": profile.starting_debt > 0
    }

    return {
        "current_step": 0,
        "current_age": profile.age,  # Initialize with player's starting age
        "years_passed": 0.0,
        "money": profile.starting_savings,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "investments": 0.0,
        "passive_income": 0.0,
        "debts": profile.starting_debt,
        "fi_score": 0.0,
        "energy": energy,
        "motivation": motivation,
        "social_life": social_life,
        "financial_knowledge": 30,
        "assets": assets,
        "risk_factors": risk_factors
    }


def generate_session_id() -> str:
    """
    Generate a unique session ID for a new game.

    Returns:
        Unique session identifier
    """
    return str(uuid.uuid4())


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between min and max.

    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def update_metric(current: int, change: int, min_val: int = 0, max_val: int = 100) -> int:
    """
    Update a life metric (energy, motivation, social) with bounds checking.

    Args:
        current: Current value
        change: Amount to change (can be negative)
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Updated value within bounds
    """
    new_value = current + change
    return int(clamp(new_value, min_val, max_val))


def calculate_investment_return(investment_amount: float, months: int, annual_return: float = 0.07) -> float:
    """
    Calculate investment returns over time.

    Args:
        investment_amount: Amount invested
        months: Number of months
        annual_return: Annual return rate (default 7%)

    Returns:
        Total value after returns
    """
    monthly_rate = annual_return / 12
    return investment_amount * ((1 + monthly_rate) ** months)


def calculate_debt_with_interest(principal: float, months: int, annual_rate: float = 0.05) -> float:
    """
    Calculate debt amount with interest.

    Args:
        principal: Initial debt amount
        months: Number of months
        annual_rate: Annual interest rate (default 5%)

    Returns:
        Total debt with interest
    """
    monthly_rate = annual_rate / 12
    return principal * ((1 + monthly_rate) ** months)


def assess_financial_health(state: GameState) -> Dict[str, str]:
    """
    Assess overall financial health and provide simple categories.

    Args:
        state: Current game state

    Returns:
        Dictionary with health assessments
    """
    assessments = {}

    # FI Score assessment
    if state.fi_score >= 100:
        assessments["fi_status"] = "financially_independent"
    elif state.fi_score >= 50:
        assessments["fi_status"] = "well_progressed"
    elif state.fi_score >= 25:
        assessments["fi_status"] = "on_track"
    else:
        assessments["fi_status"] = "early_stage"

    # Life balance assessment
    balance = calculate_balance_score(
        state.energy, state.motivation, state.social_life)
    if balance >= 70:
        assessments["balance_status"] = "healthy"
    elif balance >= 50:
        assessments["balance_status"] = "moderate"
    else:
        assessments["balance_status"] = "struggling"

    # Debt assessment
    if state.debts == 0:
        assessments["debt_status"] = "debt_free"
    elif state.debts < state.monthly_income * 3:
        assessments["debt_status"] = "manageable"
    elif state.debts < state.monthly_income * 6:
        assessments["debt_status"] = "concerning"
    else:
        assessments["debt_status"] = "critical"

    return assessments


# ==========================================
# Decision History Utilities (SQLite-based)
# ==========================================

async def get_recent_decisions(
    profile_id: int,
    db_session,
    limit: int = 5
) -> list:
    """
    Retrieve recent decision history for a player from SQLite.
    
    Args:
        profile_id: Player profile ID
        db_session: AsyncSession for database access
        limit: Maximum number of decisions to retrieve (default: 5)
        
    Returns:
        List of DecisionHistory records, ordered by step_number descending
    """
    from sqlmodel import select
    from models import DecisionHistory
    
    result = await db_session.execute(
        select(DecisionHistory)
        .where(DecisionHistory.profile_id == profile_id)
        .order_by(DecisionHistory.step_number.desc())
        .limit(limit)
    )
    
    decisions = result.scalars().all()
    return list(reversed(decisions))  # Return chronologically (oldest first)


def format_decisions_for_llm(decisions: list, include_summary: bool = False, summary_text: str = None) -> str:
    """
    Format decision history for LLM context in a structured way.
    
    Args:
        decisions: List of DecisionHistory records
        include_summary: Whether to prepend an AI-generated summary
        summary_text: Optional pre-generated summary text
        
    Returns:
        Formatted string for LLM context, matching RAG format style
    """
    if not decisions:
        return "This is the start of the player's journey."
    
    lines = []
    
    # Add summary if provided
    if include_summary and summary_text:
        lines.append("=== JOURNEY SUMMARY ===")
        lines.append(summary_text)
        lines.append("\n=== RECENT DECISIONS ===")
    else:
        lines.append("=== PLAYER'S PAST DECISIONS ===")
    
    # Format each decision
    for i, decision in enumerate(decisions, 1):
        fi_change = decision.fi_score_after - decision.fi_score_before
        money_change = decision.money_after - decision.money_before
        
        decision_text = (
            f"{i}. Step {decision.step_number}: {decision.event_type}\n"
            f"   Choice: {decision.chosen_option[:150]}\n"
            f"   Outcome: FI Score {decision.fi_score_before:.1f}% → {decision.fi_score_after:.1f}% "
            f"({fi_change:+.1f}%), Money {money_change:+.0f}€\n"
        )
        
        # Add consequence snippet if available
        if decision.consequence_narrative:
            decision_text += f"   Result: {decision.consequence_narrative[:200]}...\n"
        
        lines.append(decision_text)
    
    return "\n".join(lines)


async def create_decision_summary(
    decisions: list,
    current_age: int,
    current_fi_score: float
) -> str:
    """
    Create an AI-generated summary of decisions when history is long (>10 decisions).
    
    Args:
        decisions: List of DecisionHistory records to summarize
        current_age: Player's current age
        current_fi_score: Player's current FI score
        
    Returns:
        AI-generated summary text (or fallback summary if AI unavailable)
    """
    if len(decisions) <= 5:
        return ""  # No summary needed for short histories
    
    # Calculate key metrics
    fi_start = decisions[0].fi_score_before if decisions else 0
    fi_progress = current_fi_score - fi_start
    
    # Count major event types
    from collections import Counter
    event_counts = Counter(d.event_type for d in decisions)
    
    # Calculate average decision quality (FI score changes)
    fi_changes = [d.fi_score_after - d.fi_score_before for d in decisions]
    avg_change = sum(fi_changes) / len(fi_changes) if fi_changes else 0
    
    # Try AI summarization
    try:
        from ai_narrative import get_ai_client
        from google import genai
        
        client = get_ai_client()
        
        # Build context for AI
        decision_snippets = "\n".join([
            f"- Step {d.step_number} ({d.event_type}): {d.chosen_option[:80]} → FI {d.fi_score_after:.1f}%"
            for d in decisions[:10]  # Summarize first 10
        ])
        
        prompt = f"""Summarize this player's financial journey in 2-3 sentences:

Player is now age {current_age} with FI Score {current_fi_score:.1f}% (started at {fi_start:.1f}%).
Average decision impact: {avg_change:+.1f}% FI change per choice.

Key decisions:
{decision_snippets}

Write a concise narrative summary focusing on their financial trajectory and decision patterns."""

        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        
        summary = response.text.strip()
        return summary
        
    except Exception as e:
        print(f"⚠️ AI summary failed: {e}, using fallback")
        
        # Fallback: Rule-based summary
        trend = "improving" if fi_progress > 5 else "stable" if fi_progress > -5 else "declining"
        top_events = ", ".join([f"{count} {event}" for event, count in event_counts.most_common(3)])
        
        return (
            f"Journey started at FI Score {fi_start:.1f}%, now at {current_fi_score:.1f}% ({trend}). "
            f"Encountered {len(decisions)} decisions including {top_events}. "
            f"Average decision impact: {avg_change:+.1f}% per choice."
        )


async def get_decision_context_for_llm(
    profile_id: int,
    db_session,
    current_age: int,
    current_fi_score: float,
    max_recent: int = 3
) -> str:
    """
    Get formatted decision history for LLM context with automatic summarization.
    
    Strategy:
    - If ≤10 decisions: Show last 5 decisions
    - If >10 decisions: Show AI summary of first (n-3) + last 3 raw decisions
    
    Args:
        profile_id: Player profile ID
        db_session: AsyncSession for database access
        current_age: Player's current age
        current_fi_score: Player's current FI score
        max_recent: Number of recent raw decisions to show (default: 3)
        
    Returns:
        Formatted context string for LLM prompt
    """
    from models import DecisionHistory
    from sqlmodel import select, func
    
    # Count total decisions
    count_result = await db_session.execute(
        select(func.count(DecisionHistory.id))
        .where(DecisionHistory.profile_id == profile_id)
    )
    total_decisions = count_result.scalar()
    
    if total_decisions == 0:
        return "This is the start of the player's journey."
    
    # Short history: Just show last 5
    if total_decisions <= 10:
        decisions = await get_recent_decisions(profile_id, db_session, limit=5)
        return format_decisions_for_llm(decisions, include_summary=False)
    
    # Long history: Summary + recent decisions
    else:
        # Get all decisions for summary
        all_result = await db_session.execute(
            select(DecisionHistory)
            .where(DecisionHistory.profile_id == profile_id)
            .order_by(DecisionHistory.step_number)
        )
        all_decisions = all_result.scalars().all()
        
        # Get recent decisions
        recent_decisions = await get_recent_decisions(profile_id, db_session, limit=max_recent)
        
        # Generate summary of earlier decisions
        earlier_decisions = [d for d in all_decisions if d not in recent_decisions]
        summary = await create_decision_summary(earlier_decisions, current_age, current_fi_score)
        
        return format_decisions_for_llm(
            recent_decisions,
            include_summary=True,
            summary_text=summary
        )
