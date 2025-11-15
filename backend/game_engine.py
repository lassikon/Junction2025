"""
Game engine for LifeSim - handles decision processing and event generation.

This module contains the core game logic:
- Processing player decisions
- Updating game state based on choices
- Generating events and options
- Triggering curveballs
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


# Event templates for different stages of the game
EVENT_TYPES = [
    "first_paycheck",
    "budget_decision",
    "investment_opportunity",
    "unexpected_expense",
    "career_opportunity",
    "lifestyle_choice",
    "housing_decision",
    "vehicle_decision",
    "debt_management",
    "emergency_fund",
    "social_event",
    "education_opportunity"
]


class DecisionEffect:
    """Represents the effects of a decision on game state"""

    def __init__(self):
        self.money_change: float = 0
        self.investment_change: float = 0
        self.debt_change: float = 0
        self.income_change: float = 0
        self.expense_change: float = 0
        self.passive_income_change: float = 0

        self.energy_change: int = 0
        self.motivation_change: int = 0
        self.social_change: int = 0
        self.knowledge_change: int = 0

        self.asset_updates: Dict = {}
        self.risk_factor_updates: Dict = {}


def apply_decision_effects(state: GameState, effect: DecisionEffect) -> None:
    """
    Apply decision effects to game state.

    Args:
        state: Current game state
        effect: DecisionEffect object with changes to apply
    """
    # Update financial metrics
    state.money += effect.money_change
    state.investments += effect.investment_change
    state.debts += effect.debt_change
    state.monthly_income += effect.income_change
    state.monthly_expenses += effect.expense_change
    state.passive_income += effect.passive_income_change

    # Convert negative cash to debt
    if state.money < 0:
        # Transfer negative balance to debt
        deficit = abs(state.money)
        state.debts += deficit
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

    # Increment step and age
    state.current_step += 1

    # Time progression: each step = 6 months
    time_per_step = 0.5  # years
    state.years_passed += time_per_step
    state.current_age = int(state.current_age + time_per_step)


def get_event_type(state: GameState, profile: PlayerProfile) -> str:
    """
    Determine the next event type based on game state and progress.

    Args:
        state: Current game state
        profile: Player profile

    Returns:
        Event type string
    """
    step = state.current_step

    # First few steps follow a progression
    if step == 0:
        return "first_paycheck"
    elif step == 1:
        return "budget_decision"
    elif step == 2:
        return "emergency_fund"

    # Check for curveball
    if should_trigger_curveball(state):
        return "curveball"

    # Weighted random selection based on current state
    weights = {
        "investment_opportunity": 2 if state.money > 5000 else 1,
        "career_opportunity": 2 if state.motivation > 60 else 1,
        "lifestyle_choice": 2 if state.social_life < 50 else 1,
        "housing_decision": 2 if step > 5 and "rental" in state.assets else 1,
        "vehicle_decision": 1 if not state.risk_factors.get("has_car") else 0,
        "debt_management": 3 if state.debts > 0 else 0,
        "social_event": 2 if state.energy > 50 else 1,
        "education_opportunity": 1 if state.financial_knowledge < 60 else 0,
    }

    available_events = [k for k, v in weights.items() if v > 0]
    event_weights = [weights[k] for k in available_events]

    if not available_events:
        return "budget_decision"

    return random.choices(available_events, weights=event_weights)[0]


def should_trigger_curveball(state: GameState) -> bool:
    """
    Determine if a curveball event should trigger.

    Args:
        state: Current game state

    Returns:
        True if curveball should trigger
    """
    # Base probability
    base_prob = 0.15

    # Increase probability based on risk factors
    if state.risk_factors.get("has_car"):
        base_prob += 0.05
    if state.risk_factors.get("has_pet"):
        base_prob += 0.05
    if state.debts > state.monthly_income * 3:
        base_prob += 0.1

    # Never on first 3 steps
    if state.current_step < 3:
        return False

    return random.random() < base_prob


def generate_curveball_event(state: GameState) -> Dict:
    """
    Generate a curveball event with options.

    Args:
        state: Current game state

    Returns:
        Dictionary with event details
    """
    curveballs = []

    # Car-related curveballs
    if state.risk_factors.get("has_car"):
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
        curveballs.append({
            "narrative": "Your pet needs urgent veterinary care. The vet bill is €800.",
            "type": "vet_bill",
            "cost": 800
        })

    # Housing curveballs
    if state.risk_factors.get("has_rental"):
        curveballs.append({
            "narrative": "Your landlord is increasing rent by €150 per month starting next month.",
            "type": "rent_increase",
            "monthly_cost": 150
        })

    # Always available curveballs
    curveballs.extend([
        {
            "narrative": "Surprise! You received a tax refund of €600.",
            "type": "tax_refund",
            "gain": 600
        },
        {
            "narrative": "Your employer announced unexpected bonuses. You receive €1,000!",
            "type": "bonus",
            "gain": 1000
        },
        {
            "narrative": "A close friend invites you on an amazing trip abroad. It would cost €1,500.",
            "type": "trip_opportunity",
            "cost": 1500
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

    # Event-specific option generators
    option_generators = {
        "first_paycheck": create_first_paycheck_options,
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

    # Life metric effects
    effect.energy_change = int(option.get("energy_change", 0))
    effect.motivation_change = int(option.get("motivation_change", 0))
    effect.social_change = int(option.get("social_change", 0))
    effect.knowledge_change = int(option.get("knowledge_change", 0))

    # Asset and risk factor updates (if provided)
    effect.asset_updates = option.get("asset_updates", {})
    effect.risk_factor_updates = option.get("risk_factor_updates", {})

    return effect
