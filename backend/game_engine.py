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
            "text": "Save 50% in emergency fund, spend the rest",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", paycheck * 0.5)
                    or setattr(e, "motivation_change", 5)
                    or setattr(e, "knowledge_change", 5),
            "explanation": "Building an emergency fund is financially wise and boosts confidence."
        },
        {
            "text": "Invest 30% in index funds, save 20%, enjoy 50%",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", paycheck * 0.2)
                    or setattr(e, "investment_change", paycheck * 0.3)
                    or setattr(e, "passive_income_change", paycheck * 0.3 * 0.005)
                    or setattr(e, "knowledge_change", 10)
                    or setattr(e, "social_change", 5),
            "explanation": "Balanced approach: investing early, saving, and enjoying life."
        },
        {
            "text": "Celebrate with friends and treat yourself",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", paycheck * 0.1)
                    or setattr(e, "social_change", 15)
                    or setattr(e, "motivation_change", 10)
                    or setattr(e, "energy_change", 5),
            "explanation": "Enjoying your hard work is important, but leaves little for savings."
        },
        {
            "text": "Save 80% aggressively for future goals",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", paycheck * 0.8)
                    or setattr(e, "motivation_change", -5)
                    or setattr(e, "social_change", -10)
                    or setattr(e, "knowledge_change", 5),
            "explanation": "Maximum savings, but may impact quality of life and relationships."
        }
    ]


def create_budget_options(state: GameState) -> List[Dict]:
    """Options for budget decision event"""
    return [
        {
            "text": "Create a detailed budget using the 50/30/20 rule",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "knowledge_change", 15)
                    or setattr(e, "motivation_change", 5),
            "explanation": "Smart budgeting helps track expenses: 50% needs, 30% wants, 20% savings."
        },
        {
            "text": "Use a budgeting app to automate tracking",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "knowledge_change", 10)
                    or setattr(e, "money_change", -5)
                    or setattr(e, "motivation_change", 10),
            "explanation": "Technology makes budgeting easier, small subscription cost."
        },
        {
            "text": "Keep rough mental track of spending",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "knowledge_change", 2),
            "explanation": "Less structure, might miss overspending patterns."
        }
    ]


def create_emergency_fund_options(state: GameState) -> List[Dict]:
    """Options for emergency fund event"""
    target = state.monthly_expenses * 3

    return [
        {
            "text": f"Save aggressively to reach 3 months expenses (€{target:.0f})",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", min(state.monthly_income * 0.4, target - state.money))
            or setattr(e, "knowledge_change", 10)
            or setattr(e, "social_change", -5),
            "explanation": "Financial security first, but requires sacrifice."
        },
        {
            "text": "Save gradually while maintaining lifestyle",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", state.monthly_income * 0.2)
                    or setattr(e, "knowledge_change", 5),
            "explanation": "Balanced approach to building emergency fund."
        },
        {
            "text": "Focus on enjoying life now, save what's left",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", state.monthly_income * 0.05)
                    or setattr(e, "social_change", 10)
                    or setattr(e, "energy_change", 5),
            "explanation": "Living well now, but vulnerable to emergencies."
        }
    ]


def create_investment_options(state: GameState) -> List[Dict]:
    """Options for investment opportunity event"""
    return [
        {
            "text": "Invest €2,000 in diversified index funds",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -2000)
                    or setattr(e, "investment_change", 2000)
                    or setattr(e, "passive_income_change", 10)
                    or setattr(e, "knowledge_change", 15),
            "explanation": "Long-term growth potential, compound returns over time."
        },
        {
            "text": "Invest €1,000 in a high-growth tech fund",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -1000)
                    or setattr(e, "investment_change", 1000)
                    or setattr(e, "passive_income_change", 8)
                    or setattr(e, "knowledge_change", 10),
            "explanation": "Higher risk but potentially higher returns."
        },
        {
            "text": "Keep savings liquid for now",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "motivation_change", -5),
            "explanation": "Playing it safe, missing growth opportunities."
        }
    ]


def create_career_options(state: GameState) -> List[Dict]:
    """Options for career opportunity event"""
    return [
        {
            "text": "Take overtime shifts for extra income",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "income_change", 400)
                    or setattr(e, "energy_change", -15)
                    or setattr(e, "social_change", -10),
            "explanation": "More money, but burnout risk and less free time."
        },
        {
            "text": "Pursue a certification course for career growth",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -800)
                    or setattr(e, "income_change", 200)
                    or setattr(e, "knowledge_change", 20)
                    or setattr(e, "motivation_change", 10),
            "explanation": "Investment in yourself, long-term income boost."
        },
        {
            "text": "Maintain current work-life balance",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "energy_change", 5)
                    or setattr(e, "social_change", 5),
            "explanation": "Prioritizing well-being over extra income."
        }
    ]


def create_lifestyle_options(state: GameState) -> List[Dict]:
    """Options for lifestyle choice event"""
    return [
        {
            "text": "Join a gym and cooking class (€60/month)",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "expense_change", 60)
                    or setattr(e, "energy_change", 15)
                    or setattr(e, "motivation_change", 10),
            "explanation": "Investing in health and skills improves overall well-being."
        },
        {
            "text": "Free outdoor activities and online resources",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "energy_change", 10)
                    or setattr(e, "knowledge_change", 5),
            "explanation": "Frugal approach to staying active and learning."
        },
        {
            "text": "Treat yourself to entertainment subscriptions (€40/month)",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "expense_change", 40)
                    or setattr(e, "motivation_change", 10)
                    or setattr(e, "social_change", 5),
            "explanation": "Entertainment value, but ongoing cost adds up."
        }
    ]


def create_debt_options(state: GameState) -> List[Dict]:
    """Options for debt management event"""
    debt_payment = min(state.debts * 0.5, state.money * 0.6)

    return [
        {
            "text": f"Pay off €{debt_payment:.0f} of debt aggressively",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -debt_payment)
            or setattr(e, "debt_change", -debt_payment)
            or setattr(e, "motivation_change", 15)
            or setattr(e, "knowledge_change", 10),
            "explanation": "Reduce debt burden and save on interest payments."
        },
        {
            "text": "Make minimum payments, invest the difference",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -debt_payment * 0.2)
                    or setattr(e, "debt_change", -debt_payment * 0.2)
                    or setattr(e, "investment_change", debt_payment * 0.3)
                    or setattr(e, "passive_income_change", 2),
            "explanation": "If interest is low, investing might yield better returns."
        },
        {
            "text": "Refinance debt at a lower interest rate",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "debt_change", state.debts * -0.05)
                    or setattr(e, "knowledge_change", 15),
            "explanation": "Smart strategy reduces total interest paid over time."
        }
    ]


def create_social_options(state: GameState) -> List[Dict]:
    """Options for social event"""
    return [
        {
            "text": "Host a potluck dinner party (€30)",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -30)
                    or setattr(e, "social_change", 15)
                    or setattr(e, "energy_change", -5)
                    or setattr(e, "motivation_change", 10),
            "explanation": "Affordable way to connect with friends and recharge."
        },
        {
            "text": "Attend expensive concert/event (€120)",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -120)
                    or setattr(e, "social_change", 20)
                    or setattr(e, "motivation_change", 15),
            "explanation": "Memorable experience, but pricey."
        },
        {
            "text": "Free community activities and meetups",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "social_change", 10)
                    or setattr(e, "energy_change", 5),
            "explanation": "Build connections without spending money."
        }
    ]


def create_education_options(state: GameState) -> List[Dict]:
    """Options for education opportunity event"""
    return [
        {
            "text": "Take online financial literacy course (€200)",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "money_change", -200)
                    or setattr(e, "knowledge_change", 25)
                    or setattr(e, "motivation_change", 10),
            "explanation": "Knowledge is power - better financial decisions ahead."
        },
        {
            "text": "Read free personal finance books and blogs",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "knowledge_change", 15)
                    or setattr(e, "motivation_change", 5),
            "explanation": "Self-directed learning, no cost."
        },
        {
            "text": "Learn by doing, skip formal education",
            "effect": DecisionEffect(),
            "setup": lambda e: setattr(e, "knowledge_change", 5),
            "explanation": "Experience teaches, but slower progress."
        }
    ]


def create_curveball_options(curveball: Dict, state: GameState) -> List[Dict]:
    """Create options for curveball events"""
    curveball_type = curveball["type"]

    if "cost" in curveball:
        cost = curveball["cost"]
        return [
            {
                "text": f"Pay from savings (€{cost})",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "money_change", -cost)
                or setattr(e, "motivation_change", -10),
                "explanation": "Depletes savings but handles the situation immediately."
            },
            {
                "text": f"Use credit/take loan (€{cost})",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "debt_change", cost)
                or setattr(e, "motivation_change", -15)
                or setattr(e, "energy_change", -5),
                "explanation": "Keeps cash but adds debt burden and interest."
            },
            {
                "text": "Try to negotiate or find cheaper alternative",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "money_change", -cost * 0.7)
                        or setattr(e, "energy_change", -10)
                        or setattr(e, "knowledge_change", 10),
                "explanation": "Time and effort needed, but saves some money."
            }
        ]
    elif "gain" in curveball:
        gain = curveball["gain"]
        return [
            {
                "text": f"Save the entire €{gain}",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "money_change", gain)
                or setattr(e, "motivation_change", 5),
                "explanation": "Boosting emergency fund or savings goal."
            },
            {
                "text": f"Invest €{gain} for long-term growth",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "investment_change", gain)
                or setattr(e, "passive_income_change", gain * 0.005)
                or setattr(e, "knowledge_change", 5),
                "explanation": "Put windfall to work for compound growth."
            },
            {
                "text": f"Treat yourself and save half (€{gain/2:.0f})",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "money_change", gain * 0.5)
                or setattr(e, "social_change", 10)
                or setattr(e, "motivation_change", 10),
                "explanation": "Balance between enjoying now and saving for later."
            }
        ]
    elif "monthly_cost" in curveball:
        monthly_cost = curveball["monthly_cost"]
        return [
            {
                "text": f"Accept the increase (€{monthly_cost}/month)",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "expense_change", monthly_cost)
                or setattr(e, "motivation_change", -10),
                "explanation": "Easiest option but increases monthly expenses."
            },
            {
                "text": "Look for alternatives or negotiate",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "expense_change", monthly_cost * 0.5)
                        or setattr(e, "energy_change", -10)
                        or setattr(e, "knowledge_change", 10),
                "explanation": "Takes effort but might reduce the impact."
            },
            {
                "text": "Cut other expenses to compensate",
                "effect": DecisionEffect(),
                "setup": lambda e: setattr(e, "expense_change", monthly_cost)
                        or setattr(e, "social_change", -10)
                        or setattr(e, "energy_change", -5),
                "explanation": "Maintain budget but sacrifice elsewhere."
            }
        ]

    return []


def setup_option_effect(option: Dict) -> DecisionEffect:
    """Helper to create and setup a DecisionEffect from option config"""
    effect = option["effect"]
    if "setup" in option:
        option["setup"](effect)
    return effect
