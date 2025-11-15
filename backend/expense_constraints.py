"""
Expense category constraints and validation for LifeSim.

This module defines minimum thresholds and health impact rules for expense categories.
Players cannot reduce expenses below certain minimums, and insufficient spending
in critical categories (like food) has negative consequences on life metrics.
"""

from typing import Dict, Tuple


# Minimum monthly expenses per category (in EUR)
# These are absolute minimums below which life becomes unsustainable
EXPENSE_MINIMUMS = {
    "housing": 300.0,      # Minimum rent (shared room/student housing)
    "food": 150.0,         # Bare minimum for basic nutrition
    "transport": 30.0,     # Public transport pass at minimum
    "utilities": 50.0,     # Basic utilities (can't turn off electricity)
    "subscriptions": 0.0,  # Optional - can be zero
    "insurance": 20.0,     # Minimum health insurance
    "other": 20.0          # Basic hygiene, personal care
}

# Thresholds where spending affects health/metrics
# Below these values, you start experiencing negative effects
EXPENSE_HEALTH_THRESHOLDS = {
    "housing": {
        "comfortable": 500.0,   # Above this = no negative effects
        "adequate": 350.0,      # Between adequate and minimum = -1 energy per month
        "minimum": 300.0        # At minimum = -2 energy, -1 social per month
    },
    "food": {
        "comfortable": 250.0,   # Above this = no negative effects, might gain energy
        "adequate": 200.0,      # Between adequate and comfortable = neutral
        "poor": 150.0           # Between poor and adequate = -1 energy per month
        # At minimum (150) = -3 energy, -1 motivation per month
    },
    "transport": {
        "comfortable": 80.0,    # Own car or flexible transport
        "adequate": 50.0,       # Public transport pass
        "minimum": 30.0         # Limited transport = -1 social per month
    }
}


def validate_expense_change(
    category: str,
    current_value: float,
    change: float,
    city: str = "Helsinki"
) -> Tuple[float, str]:
    """
    Validate an expense change and return the actual allowed change.

    Args:
        category: Expense category name
        current_value: Current expense value
        change: Requested change (can be negative)
        city: Player's city (affects minimums for housing)

    Returns:
        Tuple of (allowed_change, warning_message)
        - allowed_change: The actual change that can be applied (may be less than requested)
        - warning_message: Empty string if OK, warning message if hitting minimum
    """
    minimum = EXPENSE_MINIMUMS.get(category, 0.0)

    # Adjust minimums for expensive cities
    if category == "housing" and city.lower() in ["helsinki", "espoo", "vantaa"]:
        minimum = max(minimum, 400.0)  # Higher minimum in Helsinki area

    new_value = current_value + change

    # If trying to go below minimum, cap the reduction
    if new_value < minimum:
        allowed_change = minimum - current_value
        warning = f"Cannot reduce {category} below €{minimum:.0f}/month (minimum living standard)"
        return allowed_change, warning

    return change, ""


def calculate_health_impact(
    category: str,
    current_value: float,
    change: float
) -> Dict[str, int]:
    """
    Calculate the impact on life metrics from expense changes.

    Args:
        category: Expense category name
        current_value: Current expense value before change
        change: The change being applied

    Returns:
        Dictionary with metric changes: {"energy": -2, "motivation": -1, ...}
    """
    new_value = current_value + change
    impact = {}

    # Only certain categories have health impacts
    if category not in EXPENSE_HEALTH_THRESHOLDS:
        return impact

    thresholds = EXPENSE_HEALTH_THRESHOLDS[category]

    if category == "food":
        # Food has the most significant health impact
        if new_value <= thresholds["poor"]:
            # At minimum food budget
            impact["energy"] = -3
            impact["motivation"] = -1
        elif new_value <= thresholds["adequate"]:
            # Poor food budget
            impact["energy"] = -1
        elif new_value >= thresholds["comfortable"]:
            # Good food budget - might gain energy if coming from lower
            if current_value < thresholds["comfortable"]:
                impact["energy"] = 1

    elif category == "housing":
        if new_value <= thresholds["minimum"]:
            # Minimum housing (shared room, poor conditions)
            impact["energy"] = -2
            impact["social"] = -1
        elif new_value <= thresholds["adequate"]:
            # Adequate but not comfortable
            impact["energy"] = -1

    elif category == "transport":
        if new_value <= thresholds["minimum"]:
            # Very limited transport = harder to socialize
            impact["social"] = -1

    return impact


def calculate_monthly_health_impact(expenses: Dict[str, float]) -> Dict[str, int]:
    """
    Calculate ongoing monthly health impact from current expense levels.
    Called each month to apply continuous effects of low spending.

    Args:
        expenses: Dictionary with current expense values per category

    Returns:
        Dictionary with metric changes to apply this month
    """
    impact = {
        "energy": 0,
        "motivation": 0,
        "social": 0,
        "knowledge": 0
    }

    # Check food spending
    food = expenses.get("food", 0)
    if food <= EXPENSE_HEALTH_THRESHOLDS["food"]["poor"]:
        impact["energy"] -= 2  # Chronic malnutrition
        impact["motivation"] -= 1
    elif food <= EXPENSE_HEALTH_THRESHOLDS["food"]["adequate"]:
        impact["energy"] -= 1  # Poor diet

    # Check housing quality
    housing = expenses.get("housing", 0)
    if housing <= EXPENSE_HEALTH_THRESHOLDS["housing"]["minimum"]:
        impact["energy"] -= 1  # Poor sleep, stress from bad housing
        impact["social"] -= 1  # Embarrassed to invite people over

    # Check transport availability
    transport = expenses.get("transport", 0)
    if transport <= EXPENSE_HEALTH_THRESHOLDS["transport"]["minimum"]:
        impact["social"] -= 1  # Hard to meet people, attend events

    return impact


def get_expense_warning(category: str, value: float) -> str:
    """
    Get a warning message if expense is dangerously low.

    Args:
        category: Expense category name
        value: Current expense value

    Returns:
        Warning message or empty string
    """
    if category not in EXPENSE_HEALTH_THRESHOLDS:
        return ""

    thresholds = EXPENSE_HEALTH_THRESHOLDS[category]
    minimum = EXPENSE_MINIMUMS[category]

    if category == "food":
        if value <= minimum:
            return "⚠️ Your food budget is at the absolute minimum. You're not eating enough - this is severely impacting your energy and health."
        elif value <= thresholds["poor"]:
            return "⚠️ Your food budget is very low. Poor nutrition is affecting your energy levels."
        elif value <= thresholds["adequate"]:
            return "Your food budget is adequate but limited. Consider increasing it for better energy."

    elif category == "housing":
        if value <= minimum:
            return "⚠️ Your housing is at the bare minimum (shared room/poor conditions). This is affecting your wellbeing."
        elif value <= thresholds["adequate"]:
            return "Your housing is adequate but not comfortable. This may impact your energy and social life."

    elif category == "transport":
        if value <= minimum:
            return "⚠️ Your transport budget is minimal. This limits your ability to socialize and attend events."

    return ""


def format_expense_constraints_info() -> str:
    """
    Format expense constraint information for display or AI prompts.

    Returns:
        Formatted string explaining expense minimums and health impacts
    """
    info = """
EXPENSE CONSTRAINTS & HEALTH IMPACTS:

Minimum Monthly Expenses (cannot go below):
- Housing: €300 (€400 in Helsinki area) - Shared room minimum
- Food: €150 - Bare minimum nutrition
- Transport: €30 - Basic public transport
- Utilities: €50 - Cannot turn off electricity/water
- Insurance: €20 - Minimum health coverage
- Other: €20 - Basic hygiene/personal care
- Subscriptions: €0 - Fully optional

Health Impact Thresholds:

FOOD (most critical):
- Below €150: -3 energy, -1 motivation per month (malnutrition)
- €150-200: -1 energy per month (poor diet)
- €200-250: Adequate (neutral)
- Above €250: Comfortable (may gain +1 energy)

HOUSING:
- €300-350: -2 energy, -1 social per month (poor conditions)
- €350-500: -1 energy per month (not comfortable)
- Above €500: Comfortable (neutral)

TRANSPORT:
- Below €50: -1 social per month (limited mobility)
- €50-80: Adequate (neutral)
- Above €80: Comfortable (neutral)

⚠️ WARNING: Cutting expenses saves money but has real consequences on your wellbeing!
"""
    return info
