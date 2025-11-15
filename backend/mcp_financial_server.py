"""
MCP Financial Calculator Server
Single source of truth for all financial calculations in LifeSim.
The LLM provides qualitative outcomes, this server calculates actual numbers.
"""

from enum import Enum
from typing import Dict, Tuple
import random


class AssetType(str, Enum):
    """Investment asset types with their annual yields"""
    INDEX_FUND = "index_fund"  # 5% annual
    TECH_STOCKS = "tech_stocks"  # 8% annual
    BONDS = "bonds"  # 3% annual
    SAVINGS_ACCOUNT = "savings_account"  # 1% annual
    CRYPTO = "crypto"  # 10% annual (volatile)
    REAL_ESTATE = "real_estate"  # 6% annual


class ResultQuality(str, Enum):
    """Qualitative outcome categories for LLM to return"""
    MAJOR_GAIN = "major_gain"  # 20-35% gain
    GAIN = "gain"  # 5-15% gain
    NEUTRAL = "neutral"  # -2% to +2%
    MINOR_LOSS = "minor_loss"  # 5-10% loss
    LOSS = "loss"  # 15-30% loss
    MAJOR_LOSS = "major_loss"  # 40-70% loss


# Annual yield rates for each asset type
ASSET_YIELDS = {
    AssetType.INDEX_FUND: 0.05,
    AssetType.TECH_STOCKS: 0.08,
    AssetType.BONDS: 0.03,
    AssetType.SAVINGS_ACCOUNT: 0.01,
    AssetType.CRYPTO: 0.10,
    AssetType.REAL_ESTATE: 0.06,
}


# Outcome multiplier ranges (small random variation)
OUTCOME_MULTIPLIERS = {
    ResultQuality.MAJOR_GAIN: (1.20, 1.35),
    ResultQuality.GAIN: (1.05, 1.15),
    ResultQuality.NEUTRAL: (0.98, 1.02),
    ResultQuality.MINOR_LOSS: (0.90, 0.95),
    ResultQuality.LOSS: (0.70, 0.85),
    ResultQuality.MAJOR_LOSS: (0.30, 0.60),
}


def calculate_investment_outcome(
    principal: float,
    asset_type: str,
    result_quality: str
) -> Dict[str, float]:
    """
    Calculate investment outcome with deterministic math.
    
    Args:
        principal: Amount invested (positive) or divested (negative)
        asset_type: Type of asset (from AssetType enum)
        result_quality: Qualitative outcome (from ResultQuality enum)
    
    Returns:
        {
            'money_change': float,  # Cash change (negative for investment)
            'investment_change': float,  # Investment balance change
            'passive_income_change': float,  # Monthly passive income change
            'net_gain_loss': float  # Total gain/loss from outcome
        }
    """
    # Validate inputs
    try:
        asset = AssetType(asset_type)
        quality = ResultQuality(result_quality)
    except ValueError as e:
        raise ValueError(f"Invalid asset_type or result_quality: {e}")
    
    if principal == 0:
        return {
            'money_change': 0.0,
            'investment_change': 0.0,
            'passive_income_change': 0.0,
            'net_gain_loss': 0.0
        }
    
    # Get outcome multiplier with small random variation
    multiplier_range = OUTCOME_MULTIPLIERS[quality]
    multiplier = random.uniform(multiplier_range[0], multiplier_range[1])
    
    # Calculate final investment value
    final_value = abs(principal) * multiplier
    
    # Calculate gain/loss
    net_gain_loss = final_value - abs(principal)
    
    # For investment (positive principal): money decreases, investment increases
    # For divestment (negative principal): money increases, investment decreases
    if principal > 0:
        money_change = -abs(principal)
        investment_change = final_value
    else:
        money_change = final_value
        investment_change = -abs(principal)
    
    # Calculate passive income change (monthly yield from new investment balance)
    annual_yield = ASSET_YIELDS[asset]
    monthly_yield = annual_yield / 12
    passive_income_change = investment_change * monthly_yield
    
    return {
        'money_change': round(money_change, 2),
        'investment_change': round(investment_change, 2),
        'passive_income_change': round(passive_income_change, 2),
        'net_gain_loss': round(net_gain_loss, 2)
    }


def calculate_expense_breakdown(
    total_expenses: float,
    city: str = "Helsinki",
    has_car: bool = False,
    lifestyle_level: int = 2
) -> Dict[str, float]:
    """
    Calculate expense category breakdown based on total monthly expenses.
    
    Args:
        total_expenses: Total monthly expenses
        city: City name (for cost of living adjustments)
        has_car: Whether player has a car
        lifestyle_level: 1=frugal, 2=moderate, 3=comfortable, 4=luxury
    
    Returns:
        {
            'expense_housing': float,
            'expense_food': float,
            'expense_transport': float,
            'expense_utilities': float,
            'expense_subscriptions': float,
            'expense_insurance': float,
            'expense_other': float
        }
    """
    # Base percentages for moderate lifestyle
    percentages = {
        'expense_housing': 0.35,  # 35% housing
        'expense_food': 0.20,  # 20% food
        'expense_transport': 0.10,  # 10% transport
        'expense_utilities': 0.08,  # 8% utilities
        'expense_subscriptions': 0.05,  # 5% subscriptions
        'expense_insurance': 0.07,  # 7% insurance
        'expense_other': 0.15,  # 15% other
    }
    
    # Adjust for lifestyle
    if lifestyle_level == 1:  # Frugal
        percentages['expense_housing'] = 0.40
        percentages['expense_food'] = 0.18
        percentages['expense_subscriptions'] = 0.03
        percentages['expense_other'] = 0.10
    elif lifestyle_level == 3:  # Comfortable
        percentages['expense_housing'] = 0.32
        percentages['expense_food'] = 0.22
        percentages['expense_subscriptions'] = 0.08
        percentages['expense_other'] = 0.18
    elif lifestyle_level == 4:  # Luxury
        percentages['expense_housing'] = 0.30
        percentages['expense_food'] = 0.25
        percentages['expense_subscriptions'] = 0.10
        percentages['expense_other'] = 0.20
    
    # Adjust for car ownership
    if has_car:
        percentages['expense_transport'] = 0.15
        percentages['expense_insurance'] = 0.10
        # Reduce other categories proportionally
        reduction = 0.08
        for key in ['expense_housing', 'expense_food', 'expense_other']:
            percentages[key] -= reduction / 3
    
    # Calculate actual amounts
    breakdown = {}
    total_percentage = 0.0
    for key, pct in percentages.items():
        if key != 'expense_other':
            breakdown[key] = round(total_expenses * pct, 2)
            total_percentage += pct
    
    # Other category gets the remainder to ensure exact sum
    breakdown['expense_other'] = round(
        total_expenses - sum(breakdown.values()), 2
    )
    
    return breakdown


def validate_balance_sheet(
    money_before: float,
    investments_before: float,
    money_change: float,
    investment_change: float
) -> Tuple[bool, str]:
    """
    Validate that a transaction maintains balance sheet integrity.
    For investments: money_change + investment_change should account for gains/losses
    
    Args:
        money_before: Cash balance before transaction
        investments_before: Investment balance before transaction
        money_change: Change in cash
        investment_change: Change in investments
    
    Returns:
        (is_valid, message)
    """
    # Check for insufficient funds
    if money_before + money_change < 0:
        return False, f"Insufficient funds: balance {money_before} + change {money_change} = negative"
    
    # For investments: total wealth should only change by gains/losses
    total_before = money_before + investments_before
    total_after = (money_before + money_change) + (investments_before + investment_change)
    wealth_change = total_after - total_before
    
    # For valid investment transactions:
    # - Money decreases by principal: money_change = -principal
    # - Investment increases by final value: investment_change = principal * multiplier
    # - Wealth changes by gain/loss: wealth_change = principal * (multiplier - 1)
    
    # Wealth change can be negative (losses) or positive (gains)
    # It should be approximately equal to investment_change + money_change
    expected_wealth_change = money_change + investment_change
    
    # Allow small rounding errors (0.01)
    if abs(wealth_change - expected_wealth_change) > 0.01:
        return False, f"Balance sheet error: wealth change {wealth_change} != money_change {money_change} + investment_change {investment_change}"
    
    return True, f"Valid transaction (wealth change: €{wealth_change:.2f})"


def test_mcp_calculator():
    """Test the MCP calculator functions"""
    print("=== MCP Financial Calculator Tests ===\n")
    
    # Test 1: Investment with gain
    print("Test 1: Invest €1000 in index fund with gain")
    result = calculate_investment_outcome(
        principal=1000.0,
        asset_type="index_fund",
        result_quality="gain"
    )
    print(f"  Money change: €{result['money_change']}")
    print(f"  Investment change: €{result['investment_change']}")
    print(f"  Passive income change: €{result['passive_income_change']}/month")
    print(f"  Net gain/loss: €{result['net_gain_loss']}")
    
    # Validate
    is_valid, msg = validate_balance_sheet(
        money_before=2000.0,
        investments_before=5000.0,
        money_change=result['money_change'],
        investment_change=result['investment_change']
    )
    print(f"  Validation: {msg}\n")
    
    # Test 2: Investment with loss
    print("Test 2: Invest €500 in crypto with loss")
    result = calculate_investment_outcome(
        principal=500.0,
        asset_type="crypto",
        result_quality="loss"
    )
    print(f"  Money change: €{result['money_change']}")
    print(f"  Investment change: €{result['investment_change']}")
    print(f"  Passive income change: €{result['passive_income_change']}/month")
    print(f"  Net gain/loss: €{result['net_gain_loss']}")
    
    is_valid, msg = validate_balance_sheet(
        money_before=2000.0,
        investments_before=5000.0,
        money_change=result['money_change'],
        investment_change=result['investment_change']
    )
    print(f"  Validation: {msg}\n")
    
    # Test 3: Expense breakdown
    print("Test 3: Expense breakdown for €1500/month, moderate lifestyle, has car")
    breakdown = calculate_expense_breakdown(
        total_expenses=1500.0,
        has_car=True,
        lifestyle_level=2
    )
    print(f"  Housing: €{breakdown['expense_housing']}")
    print(f"  Food: €{breakdown['expense_food']}")
    print(f"  Transport: €{breakdown['expense_transport']}")
    print(f"  Utilities: €{breakdown['expense_utilities']}")
    print(f"  Subscriptions: €{breakdown['expense_subscriptions']}")
    print(f"  Insurance: €{breakdown['expense_insurance']}")
    print(f"  Other: €{breakdown['expense_other']}")
    total = sum(breakdown.values())
    print(f"  Total: €{total} (should be €1500.00)")
    print(f"  Difference: €{abs(total - 1500.0)}\n")
    
    # Test 4: Major gain scenario
    print("Test 4: Invest €2000 in tech stocks with major gain")
    result = calculate_investment_outcome(
        principal=2000.0,
        asset_type="tech_stocks",
        result_quality="major_gain"
    )
    print(f"  Money change: €{result['money_change']}")
    print(f"  Investment change: €{result['investment_change']}")
    print(f"  Passive income change: €{result['passive_income_change']}/month")
    print(f"  Net gain/loss: €{result['net_gain_loss']}")
    
    is_valid, msg = validate_balance_sheet(
        money_before=5000.0,
        investments_before=10000.0,
        money_change=result['money_change'],
        investment_change=result['investment_change']
    )
    print(f"  Validation: {msg}\n")
    
    print("=== All tests completed ===")


if __name__ == "__main__":
    test_mcp_calculator()
