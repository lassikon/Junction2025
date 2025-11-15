"""
Game engine for LifeSim - handles decision processing and event generation.

This module contains the core game logic:
- Processing player decisions
- Updating game state based on choices
- Generating events and options
- Monthly phase-based progression (3 steps per month)
"""

from typing import Dict, List, Tuple, Optional
import random
from models import GameState, PlayerProfile, RiskAttitude
from utils import (
    calculate_fi_score,
    update_metric,
    calculate_balance_score,
    clamp
)


# Event types organized by month phase
PHASE_1_EVENTS = [
    "monthly_budget",
    "savings_decision",
    "investment_planning",
    "debt_payment_plan",
    "income_review"
]

PHASE_2_3_EVENTS = [
    "social_event",
    "small_purchase",
    "minor_emergency",
    "daily_choice",
    "entertainment_option",
    "maintenance_issue",
    "side_hustle_opportunity",
    "unexpected_expense"
]


def get_month_phase_name(phase: int) -> str:
    """Get descriptive name for month phase"""
    return {1: "Early", 2: "Mid", 3: "Late"}.get(phase, "Early")


def get_current_month_name(months_passed: int) -> str:
    """Get month name from months passed"""
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    return month_names[months_passed % 12]


class DecisionEffect:
    """Represents the effects of a decision on game state"""

    def __init__(self):
        self.money_change: float = 0
        self.investment_change: float = 0
        self.debt_change: float = 0
        self.income_change: float = 0
        self.expense_change: float = 0
        self.passive_income_change: float = 0

        # Detailed expense category changes
        self.expense_housing_change: float = 0
        self.expense_food_change: float = 0
        self.expense_transport_change: float = 0
        self.expense_utilities_change: float = 0
        self.expense_subscriptions_change: float = 0
        self.expense_insurance_change: float = 0
        self.expense_other_change: float = 0

        self.energy_change: int = 0
        self.motivation_change: int = 0
        self.social_change: int = 0
        self.knowledge_change: int = 0

        self.asset_updates: Dict = {}
        self.risk_factor_updates: Dict = {}


def create_transaction_description(effect: DecisionEffect) -> str:
    """
    Create a human-readable description of financial changes.

    Args:
        effect: DecisionEffect object with changes

    Returns:
        Formatted description string
    """
    changes = []

    # One-time changes
    if effect.money_change != 0:
        sign = "+" if effect.money_change > 0 else ""
        changes.append(f"Cash {sign}€{effect.money_change:.0f}")

    if effect.investment_change != 0:
        sign = "+" if effect.investment_change > 0 else ""
        changes.append(f"Investments {sign}€{effect.investment_change:.0f}")

    if effect.debt_change != 0:
        sign = "+" if effect.debt_change > 0 else ""
        changes.append(f"Debt {sign}€{effect.debt_change:.0f}")

    # Monthly recurring changes
    if effect.income_change != 0:
        sign = "+" if effect.income_change > 0 else ""
        changes.append(f"Monthly Income {sign}€{effect.income_change:.0f}/mo")

    if effect.expense_change != 0:
        sign = "+" if effect.expense_change > 0 else ""
        changes.append(
            f"Monthly Expenses {sign}€{effect.expense_change:.0f}/mo")

    if effect.passive_income_change != 0:
        sign = "+" if effect.passive_income_change > 0 else ""
        changes.append(
            f"Passive Income {sign}€{effect.passive_income_change:.0f}/mo")

    return "; ".join(changes) if changes else "No financial changes"


def apply_monthly_cash_flow(state: GameState) -> Dict:
    """
    Apply monthly income and expenses at the start of each month (phase 1 only).

    Args:
        state: Current game state

    Returns:
        Dictionary with cash flow transaction details
    """
    # Only apply on phase 1 (start of month)
    if state.month_phase != 1:
        return {
            "cash_change": 0,
            "income_received": 0,
            "expenses_paid": 0,
            "debt_from_deficit": 0,
            "cash_balance": state.money,
            "applied": False
        }

    # Calculate total monthly income (salary + passive income)
    total_income = state.monthly_income + state.passive_income

    # Apply income and expenses for the full month
    state.money += total_income
    state.money -= state.monthly_expenses

    print(
        f"💰 MONTHLY CASH FLOW (New Month - {get_current_month_name(state.months_passed)}):")
    print(f"  Income: €{total_income:.0f}")
    print(f"  Expenses: €{state.monthly_expenses:.0f}")
    print(f"  Net: €{total_income - state.monthly_expenses:.0f}")
    print(f"  Cash balance: €{state.money:.0f}")

    # Convert negative cash to debt if needed
    debt_from_deficit = 0
    if state.money < 0:
        deficit = abs(state.money)
        state.debts += deficit
        debt_from_deficit = deficit
        state.money = 0
        print(
            f"💳 Converted €{deficit:.0f} negative cash to debt. Total debt now: €{state.debts:.0f}")

    return {
        "cash_change": total_income - state.monthly_expenses,
        "income_received": total_income,
        "expenses_paid": state.monthly_expenses,
        "debt_from_deficit": debt_from_deficit,
        "cash_balance": state.money,
        "applied": True
    }


def apply_decision_effects(state: GameState, effect: DecisionEffect) -> Dict:
    """
    Apply decision effects to game state and return transaction summary.

    Args:
        state: Current game state
        effect: DecisionEffect object with changes to apply

    Returns:
        Dictionary with transaction details for logging
    """
    # Store changes before applying
    cash_change = effect.money_change
    investment_change = effect.investment_change
    debt_change = effect.debt_change

    # Update financial metrics
    state.money += effect.money_change
    state.investments += effect.investment_change
    state.debts += effect.debt_change
    state.monthly_income += effect.income_change
    state.monthly_expenses += effect.expense_change
    state.passive_income += effect.passive_income_change

    # Update expense category breakdowns
    state.expense_housing += effect.expense_housing_change
    state.expense_food += effect.expense_food_change
    state.expense_transport += effect.expense_transport_change
    state.expense_utilities += effect.expense_utilities_change
    state.expense_subscriptions += effect.expense_subscriptions_change
    state.expense_insurance += effect.expense_insurance_change
    state.expense_other += effect.expense_other_change

    # Recalculate total monthly expenses from categories
    state.monthly_expenses = (state.expense_housing + state.expense_food +
                              state.expense_transport + state.expense_utilities +
                              state.expense_subscriptions + state.expense_insurance +
                              state.expense_other)

    # Convert negative cash to debt
    if state.money < 0:
        # Transfer negative balance to debt
        deficit = abs(state.money)
        state.debts += deficit
        debt_change += deficit  # Update debt_change to reflect conversion
        state.money = 0
        print(
            f"💳 Converted €{deficit:.0f} negative cash to debt. Total debt now: €{state.debts:.0f}")

    # Update life metrics with bounds checking
    state.energy = update_metric(state.energy, effect.energy_change)
    state.motivation = update_metric(
        state.motivation, effect.motivation_change)
    state.social_life = update_metric(state.social_life, effect.social_change)
    state.financial_knowledge = update_metric(
        state.financial_knowledge, effect.knowledge_change)

    # Update assets
    for key, value in effect.asset_updates.items():
        if value is None and key in state.assets:
            del state.assets[key]
        elif value is not None:
            state.assets[key] = value

    # Update risk factors
    for key, value in effect.risk_factor_updates.items():
        state.risk_factors[key] = value

    # Recalculate FI score
    state.fi_score = calculate_fi_score(
        state.passive_income, state.monthly_expenses)

    # Increment step
    state.current_step += 1

    # Advance month phase (1 -> 2 -> 3 -> 1)
    state.month_phase += 1
    if state.month_phase > 3:
        state.month_phase = 1
        state.months_passed += 1

        # Update age every 12 months
        if state.months_passed % 12 == 0:
            state.current_age += 1

        state.years_passed = state.months_passed / 12.0

    print(
        f"⏰ TIME: Step {state.current_step}, Month {state.months_passed} (Phase {state.month_phase}/3)")

    # Return transaction summary
    return {
        "cash_change": cash_change,
        "investment_change": investment_change,
        "debt_change": debt_change,
        "monthly_income_change": effect.income_change,
        "monthly_expense_change": effect.expense_change,
        "passive_income_change": effect.passive_income_change,
        "expense_housing_change": effect.expense_housing_change,
        "expense_food_change": effect.expense_food_change,
        "expense_transport_change": effect.expense_transport_change,
        "expense_utilities_change": effect.expense_utilities_change,
        "expense_subscriptions_change": effect.expense_subscriptions_change,
        "expense_insurance_change": effect.expense_insurance_change,
        "expense_other_change": effect.expense_other_change,
        "cash_balance": state.money,
        "investment_balance": state.investments,
        "debt_balance": state.debts,
        "monthly_income_total": state.monthly_income,
        "monthly_expense_total": state.monthly_expenses,
        "passive_income_total": state.passive_income,
        "description": create_transaction_description(effect)
    }


def get_event_type(state: GameState, profile: PlayerProfile) -> str:
    """
    Determine the next event type based on month phase and game state.

    Args:
        state: Current game state
        profile: Player profile

    Returns:
        Event type string
    """
    phase = state.month_phase
    step = state.current_step

    # Phase 1 (Early Month): Budget planning and major financial decisions
    if phase == 1:
        # Check for debt
        if state.debts > state.monthly_income * 2:
            return "debt_payment_plan"

        # Regular phase 1 events (removed first_paycheck special handling)
        return random.choice(PHASE_1_EVENTS)

    # Phase 2 & 3 (Mid/Late Month): Smaller daily events and spending decisions
    else:
        # Check for curveball (lower probability for smaller events)
        if should_trigger_curveball(state):
            return "curveball"

        # Weighted selection based on state
        weights = {
            "social_event": 2 if state.energy > 50 else 1,
            "small_purchase": 2 if state.money > state.monthly_expenses else 1,
            "minor_emergency": 1,
            "daily_choice": 2,
            "entertainment_option": 2 if state.social_life < 60 else 1,
            "maintenance_issue": 2 if state.risk_factors.get("has_car") else 1,
            "side_hustle_opportunity": 1 if state.motivation > 60 else 0,
            "unexpected_expense": 1
        }

        available_events = [k for k, v in weights.items() if v > 0]
        event_weights = [weights[k] for k in available_events]

        return random.choices(available_events, weights=event_weights)[0]


def should_trigger_curveball(state: GameState) -> bool:
    """
    Determine if a curveball event should trigger.
    Lower probability for phase 2/3 since events are smaller.

    Args:
        state: Current game state

    Returns:
        True if curveball should trigger
    """
    # Base probability (lower for phase 2/3)
    base_prob = 0.08 if state.month_phase in [2, 3] else 0.15

    # Increase probability based on risk factors
    if state.risk_factors.get("has_car"):
        base_prob += 0.03
    if state.risk_factors.get("has_pet"):
        base_prob += 0.03
    if state.debts > state.monthly_income * 3:
        base_prob += 0.05

    # Never on first month
    if state.months_passed < 1:
        return False

    return random.random() < base_prob


def generate_curveball_event(state: GameState) -> Dict:
    """
    Generate a curveball event with options.
    Scales costs based on month phase (smaller for phase 2/3).

    Args:
        state: Current game state

    Returns:
        Dictionary with event details
    """
    # Scale factor for phase 2/3 events (smaller costs)
    scale = 0.4 if state.month_phase in [2, 3] else 1.0

    curveballs = []

    # Car-related curveballs
    if state.risk_factors.get("has_car"):
        if scale < 1.0:
            # Smaller car issues for phase 2/3
            curveballs.append({
                "narrative": "Your car needs a minor repair. The mechanic quotes €" + str(int(250 * scale)) + ".",
                "type": "car_repair",
                "cost": 250 * scale
            })
        else:
            # Larger issues for phase 1
            curveballs.extend([
                {
                    "narrative": "Your car suddenly breaks down and needs urgent repairs. The mechanic quotes €1,200.",
                    "type": "car_repair",
                    "cost": 1200
                },
                {
                    "narrative": "Your car insurance premium is increasing by 30% next month.",
                    "type": "insurance_increase",
                    "monthly_cost": 60
                }
            ])

    # Pet-related curveballs
    if state.risk_factors.get("has_pet"):
        cost = 800 * scale
        curveballs.append({
            "narrative": f"Your pet needs veterinary care. The vet bill is €{int(cost)}.",
            "type": "vet_bill",
            "cost": cost
        })

    # Always available curveballs (scaled for phase)
    curveballs.extend([
        {
            "narrative": f"Surprise! You received €{int(400 * scale)} from a side gig payment.",
            "type": "bonus",
            "gain": 400 * scale
        },
        {
            "narrative": f"Your phone/laptop needs an urgent repair costing €{int(300 * scale)}.",
            "type": "tech_repair",
            "cost": 300 * scale
        }
    ])

    # Only big opportunities in phase 1
    if scale >= 1.0:
        curveballs.extend([
            {
                "narrative": "Surprise! You received a tax refund of €600.",
                "type": "tax_refund",
                "gain": 600
            },
            {
                "narrative": "Your employer announced unexpected bonuses. You receive €1,000!",
                "type": "bonus_large",
                "gain": 1000
            }
        ])

    return random.choice(curveballs)


def create_decision_options(event_type: str, state: GameState, curveball: Optional[Dict] = None) -> List[Dict]:
    """
    Create decision options based on event type.

    Args:
        event_type: Type of event
        state: Current game state
        curveball: Optional curveball event details

    Returns:
        List of option dictionaries with text and effects
    """
    if event_type == "curveball" and curveball:
        return create_curveball_options(curveball, state)

    # Event-specific option generators (removed first_paycheck - no longer used)
    option_generators = {
        "budget_decision": create_budget_options,
        "emergency_fund": create_emergency_fund_options,
        "investment_opportunity": create_investment_options,
        "career_opportunity": create_career_options,
        "lifestyle_choice": create_lifestyle_options,
        "debt_management": create_debt_options,
        "social_event": create_social_options,
        "education_opportunity": create_education_options,
    }

    generator = option_generators.get(event_type, create_budget_options)
    return generator(state)


def create_first_paycheck_options(state: GameState) -> List[Dict]:
    """Options for first paycheck event"""
    paycheck = state.monthly_income

    return [
        {
            "fallback_text": "Save 50% in emergency fund, spend the rest",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", paycheck * 0.5)
            or setattr(e, "motivation_change", 5)
            or setattr(e, "knowledge_change", 5),
            "explanation": f"Save €{paycheck * 0.5:.0f} (50%) for emergencies, use the rest for living"
        },
        {
            "fallback_text": "Invest 30% in index funds, save 20%, enjoy 50%",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", paycheck * 0.2)
            or setattr(e, "investment_change", paycheck * 0.3)
            or setattr(e, "passive_income_change", paycheck * 0.3 * 0.005)
            or setattr(e, "knowledge_change", 10)
            or setattr(e, "social_change", 5),
            "explanation": f"Invest €{paycheck * 0.3:.0f} (30%), save €{paycheck * 0.2:.0f} (20%), spend rest on lifestyle"
        },
        {
            "fallback_text": "Celebrate with friends and treat yourself",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", paycheck * 0.1)
            or setattr(e, "social_change", 15)
            or setattr(e, "motivation_change", 10)
            or setattr(e, "energy_change", 5),
            "explanation": f"Celebrate big! Save only €{paycheck * 0.1:.0f} (10%), enjoy the moment with friends"
        },
        {
            "fallback_text": "Save 80% aggressively for future goals",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", paycheck * 0.8)
            or setattr(e, "motivation_change", -5)
            or setattr(e, "social_change", -10)
            or setattr(e, "knowledge_change", 5),
            "explanation": f"Maximize savings: put away €{paycheck * 0.8:.0f} (80%) for financial goals"
        }
    ]


def create_budget_options(state: GameState) -> List[Dict]:
    """Options for budget decision event"""
    return [
        {
            "fallback_text": "Create a detailed budget using the 50/30/20 rule",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "knowledge_change", 15)
            or setattr(e, "motivation_change", 5),
            "explanation": "Track expenses with 50% for needs, 30% for wants, 20% for savings"
        },
        {
            "fallback_text": "Use a budgeting app to automate tracking",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "knowledge_change", 10)
            or setattr(e, "money_change", -5)
            or setattr(e, "motivation_change", 10),
            "explanation": "Subscribe to a budgeting app (€5) for automated expense tracking"
        },
        {
            "fallback_text": "Keep rough mental track of spending",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "knowledge_change", 2),
            "explanation": "Casual approach: no formal budget, just estimate spending mentally"
        }
    ]


def create_emergency_fund_options(state: GameState) -> List[Dict]:
    """Options for emergency fund event"""
    target = state.monthly_expenses * 3

    return [
        {
            "fallback_text": f"Save aggressively to reach 3 months expenses (€{target:.0f})",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", min(state.monthly_income * 0.4, target - state.money))
            or setattr(e, "knowledge_change", 10)
            or setattr(e, "social_change", -5),
            "explanation": f"Save €{min(state.monthly_income * 0.4, target - state.money):.0f} (40% of income) to build emergency fund of €{target:.0f}"
        },
        {
            "fallback_text": "Save gradually while maintaining lifestyle",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", state.monthly_income * 0.2)
            or setattr(e, "knowledge_change", 5),
            "explanation": f"Save €{state.monthly_income * 0.2:.0f} (20% of income) monthly, keep lifestyle balanced"
        },
        {
            "fallback_text": "Focus on enjoying life now, save what's left",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", state.monthly_income * 0.05)
            or setattr(e, "social_change", 10)
            or setattr(e, "energy_change", 5),
            "explanation": f"Live well now, save only €{state.monthly_income * 0.05:.0f} (5%) from each paycheck"
        }
    ]


def create_investment_options(state: GameState) -> List[Dict]:
    """Options for investment opportunity event"""
    return [
        {
            "fallback_text": "Invest €2,000 in diversified index funds",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -2000)
            or setattr(e, "investment_change", 2000)
            or setattr(e, "passive_income_change", 10)
            or setattr(e, "knowledge_change", 15),
            "explanation": "Invest €2,000 in low-cost index funds for long-term compound growth"
        },
        {
            "fallback_text": "Invest €1,000 in a high-growth tech fund",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -1000)
            or setattr(e, "investment_change", 1000)
            or setattr(e, "passive_income_change", 8)
            or setattr(e, "knowledge_change", 10),
            "explanation": "Invest €1,000 in higher-risk tech sector for potential bigger returns"
        },
        {
            "fallback_text": "Keep savings liquid for now",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "motivation_change", -5),
            "explanation": "Skip investing this time, keep cash available for opportunities or emergencies"
        }
    ]


def create_career_options(state: GameState) -> List[Dict]:
    """Options for career opportunity event"""
    return [
        {
            "fallback_text": "Take overtime shifts for extra income",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "income_change", 400)
            or setattr(e, "energy_change", -15)
            or setattr(e, "social_change", -10),
            "explanation": "Work extra hours for €400 more monthly income, but sacrifice energy and social time"
        },
        {
            "fallback_text": "Pursue a certification course for career growth",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -800)
            or setattr(e, "income_change", 200)
            or setattr(e, "knowledge_change", 20)
            or setattr(e, "motivation_change", 10),
            "explanation": "Pay €800 for certification that boosts income by €200/month and opens career doors"
        },
        {
            "fallback_text": "Maintain current work-life balance",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "energy_change", 5)
            or setattr(e, "social_change", 5),
            "explanation": "Keep things as they are, prioritize well-being over extra earnings"
        }
    ]


def create_lifestyle_options(state: GameState) -> List[Dict]:
    """Options for lifestyle choice event"""
    return [
        {
            "fallback_text": "Join a gym and cooking class (€60/month)",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "expense_change", 60)
            or setattr(e, "energy_change", 15)
            or setattr(e, "motivation_change", 10),
            "explanation": "Invest €60/month in gym membership and cooking class for health and skills"
        },
        {
            "fallback_text": "Free outdoor activities and online resources",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "energy_change", 10)
            or setattr(e, "knowledge_change", 5),
            "explanation": "Stay active with free running, hiking, and YouTube fitness videos"
        },
        {
            "fallback_text": "Treat yourself to entertainment subscriptions (€40/month)",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "expense_change", 40)
            or setattr(e, "motivation_change", 10)
            or setattr(e, "social_change", 5),
            "explanation": "Subscribe to streaming services and gaming for €40/month entertainment"
        }
    ]


def create_debt_options(state: GameState) -> List[Dict]:
    """Options for debt management event"""
    debt_payment = min(state.debts * 0.5, state.money * 0.6)

    return [
        {
            "fallback_text": f"Pay off €{debt_payment:.0f} of debt aggressively",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -debt_payment)
            or setattr(e, "debt_change", -debt_payment)
            or setattr(e, "motivation_change", 15)
            or setattr(e, "knowledge_change", 10),
            "explanation": f"Pay €{debt_payment:.0f} toward debt to reduce burden and save on interest"
        },
        {
            "fallback_text": "Make minimum payments, invest the difference",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -debt_payment * 0.2)
            or setattr(e, "debt_change", -debt_payment * 0.2)
            or setattr(e, "investment_change", debt_payment * 0.3)
            or setattr(e, "passive_income_change", 2),
            "explanation": f"Pay minimum €{debt_payment * 0.2:.0f}, invest €{debt_payment * 0.3:.0f} for potential higher returns"
        },
        {
            "fallback_text": "Refinance debt at a lower interest rate",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "debt_change", state.debts * -0.05)
            or setattr(e, "knowledge_change", 15),
            "explanation": f"Negotiate lower rate, effectively reducing debt by €{state.debts * 0.05:.0f} in interest savings"
        }
    ]


def create_social_options(state: GameState) -> List[Dict]:
    """Options for social event"""
    return [
        {
            "fallback_text": "Host a potluck dinner party (€30)",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -30)
            or setattr(e, "social_change", 15)
            or setattr(e, "energy_change", -5)
            or setattr(e, "motivation_change", 10),
            "explanation": "Spend €30 hosting friends at home for affordable quality time"
        },
        {
            "fallback_text": "Attend expensive concert/event (€120)",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -120)
            or setattr(e, "social_change", 20)
            or setattr(e, "motivation_change", 15),
            "explanation": "Splurge €120 on an amazing concert or event for memorable experience"
        },
        {
            "fallback_text": "Free community activities and meetups",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "social_change", 10)
            or setattr(e, "energy_change", 5),
            "explanation": "Join free local events, park hangouts, or community groups"
        }
    ]


def create_education_options(state: GameState) -> List[Dict]:
    """Options for education opportunity event"""
    return [
        {
            "fallback_text": "Take online financial literacy course (€200)",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -200)
            or setattr(e, "knowledge_change", 25)
            or setattr(e, "motivation_change", 10),
            "explanation": "Invest €200 in structured financial education for better money decisions"
        },
        {
            "fallback_text": "Read free personal finance books and blogs",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "knowledge_change", 15)
            or setattr(e, "motivation_change", 5),
            "explanation": "Self-study using library books and financial blogs at no cost"
        },
        {
            "fallback_text": "Learn by doing, skip formal education",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "knowledge_change", 5),
            "explanation": "Learn through real-world experience and mistakes over time"
        }
    ]


def create_curveball_options(curveball: Dict, state: GameState) -> List[Dict]:
    """Create options for curveball events"""
    curveball_type = curveball["type"]

    if "cost" in curveball:
        cost = curveball["cost"]
        return [
            {
                "fallback_text": f"Pay from savings (€{cost})",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "money_change", -cost)
                or setattr(e, "motivation_change", -10),
                "explanation": f"Use €{cost} from savings to handle this immediately"
            },
            {
                "fallback_text": f"Use credit/take loan (€{cost})",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "debt_change", cost)
                or setattr(e, "motivation_change", -15)
                or setattr(e, "energy_change", -5),
                "explanation": f"Borrow €{cost} to cover costs, pay back with interest over time"
            },
            {
                "fallback_text": "Try to negotiate or find cheaper alternative",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "money_change", -cost * 0.7)
                or setattr(e, "energy_change", -10)
                or setattr(e, "knowledge_change", 10),
                "explanation": f"Spend time finding deals, pay only €{cost * 0.7:.0f} instead"
            }
        ]
    elif "gain" in curveball:
        gain = curveball["gain"]
        return [
            {
                "fallback_text": f"Save the entire €{gain}",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "money_change", gain)
                or setattr(e, "motivation_change", 5),
                "explanation": f"Put all €{gain} windfall into savings for security"
            },
            {
                "fallback_text": f"Invest €{gain} for long-term growth",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "investment_change", gain)
                or setattr(e, "passive_income_change", gain * 0.005)
                or setattr(e, "knowledge_change", 5),
                "explanation": f"Invest €{gain} in index funds for compound growth potential"
            },
            {
                "fallback_text": f"Treat yourself and save half (€{gain/2:.0f})",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "money_change", gain * 0.5)
                or setattr(e, "social_change", 10)
                or setattr(e, "motivation_change", 10),
                "explanation": f"Enjoy €{gain/2:.0f} now, save €{gain/2:.0f} for later"
            }
        ]
    elif "monthly_cost" in curveball:
        monthly_cost = curveball["monthly_cost"]
        return [
            {
                "fallback_text": f"Accept the increase (€{monthly_cost}/month)",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "expense_change", monthly_cost)
                or setattr(e, "motivation_change", -10),
                "explanation": f"Pay the extra €{monthly_cost}/month without changes"
            },
            {
                "fallback_text": "Look for alternatives or negotiate",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "expense_change", monthly_cost * 0.5)
                or setattr(e, "energy_change", -10)
                or setattr(e, "knowledge_change", 10),
                "explanation": f"Shop around and negotiate, reduce impact to €{monthly_cost * 0.5:.0f}/month"
            },
            {
                "fallback_text": "Cut other expenses to compensate",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "expense_change", monthly_cost)
                or setattr(e, "social_change", -10)
                or setattr(e, "energy_change", -5),
                "explanation": f"Accept €{monthly_cost}/month increase but reduce spending elsewhere"
            }
        ]

    return []


def setup_option_effect(option: Dict) -> DecisionEffect:
    """Helper to create and setup a DecisionEffect from option config"""
    effect = option["effect"]
    if "setup" in option:
        option["setup"](effect)
    return effect


def setup_dynamic_option_effect(option: Dict) -> DecisionEffect:
    """
    Create a DecisionEffect from a dynamically generated option.

    Args:
        option: Dictionary with effect values from AI generation

    Returns:
        DecisionEffect object
    """
    effect = DecisionEffect()

    # Financial effects
    effect.money_change = option.get("money_change", 0)
    effect.investment_change = option.get("investment_change", 0)
    effect.debt_change = option.get("debt_change", 0)
    effect.income_change = option.get("income_change", 0)
    effect.expense_change = option.get("expense_change", 0)
    effect.passive_income_change = option.get("passive_income_change", 0)

    # Expense category effects
    effect.expense_housing_change = option.get("expense_housing_change", 0)
    effect.expense_food_change = option.get("expense_food_change", 0)
    effect.expense_transport_change = option.get("expense_transport_change", 0)
    effect.expense_utilities_change = option.get("expense_utilities_change", 0)
    effect.expense_subscriptions_change = option.get(
        "expense_subscriptions_change", 0)
    effect.expense_insurance_change = option.get("expense_insurance_change", 0)
    effect.expense_other_change = option.get("expense_other_change", 0)

    # Life metric effects
    effect.energy_change = int(option.get("energy_change", 0))
    effect.motivation_change = int(option.get("motivation_change", 0))
    effect.social_change = int(option.get("social_change", 0))
    effect.knowledge_change = int(option.get("knowledge_change", 0))

    # Asset and risk factor updates (if provided)
    effect.asset_updates = option.get("asset_updates", {})
    effect.risk_factor_updates = option.get("risk_factor_updates", {})

    return effect
