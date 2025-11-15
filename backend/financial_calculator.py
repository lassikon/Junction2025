"""
Financial Calculator Middleware
Translates LLM qualitative outcomes into MCP financial calculations
Uses MCP client to communicate with standalone MCP server
"""

from typing import Dict, Optional
from mcp_client import get_mcp_client


async def parse_llm_outcome(llm_response: Dict) -> Dict[str, float]:
    """
    Parse LLM response and calculate actual financial effects using MCP server.
    
    Args:
        llm_response: Response from LLM containing narrative and outcome
        
    Returns:
        Dictionary of calculated effects to apply to GameState
    """
    print(f"[FINANCIAL_CALC] DEBUG - Parsing LLM response:")
    print(f"  Keys in response: {llm_response.keys()}")
    
    # Check if LLM returned old format with 'effects' instead of 'outcome'
    if 'effects' in llm_response and 'outcome' not in llm_response:
        print(f"  ⚠️  LLM returned OLD format with 'effects' - prompt not updated!")
        print(f"  Using legacy effects directly without MCP calculation")
        # Return the effects as-is (old behavior)
        old_effects = llm_response['effects']
        return {
            "money_change": old_effects.get("money_change", 0),
            "investment_change": old_effects.get("investment_change", 0),
            "passive_income_change": old_effects.get("passive_income_change", 0),
            "debt_change": old_effects.get("debt_change", 0),
            "income_change": old_effects.get("income_change", 0),
            "expense_housing_change": old_effects.get("expense_housing_change", 0),
            "expense_food_change": old_effects.get("expense_food_change", 0),
            "expense_transport_change": old_effects.get("expense_transport_change", 0),
            "expense_utilities_change": old_effects.get("expense_utilities_change", 0),
            "expense_subscriptions_change": old_effects.get("expense_subscriptions_change", 0),
            "expense_insurance_change": old_effects.get("expense_insurance_change", 0),
            "expense_other_change": old_effects.get("expense_other_change", 0),
            "energy_change": old_effects.get("energy_change", 0),
            "motivation_change": old_effects.get("motivation_change", 0),
            "social_change": old_effects.get("social_change", 0),
            "knowledge_change": old_effects.get("knowledge_change", 0),
        }
    
    outcome = llm_response.get("outcome", {})
    action_type = outcome.get("action_type", "")
    
    print(f"  Outcome found: {bool(outcome)}")
    print(f"  Action type: {action_type}")
    
    # Initialize effects
    effects = {
        "money_change": 0.0,
        "investment_change": 0.0,
        "passive_income_change": 0.0,
        "debt_change": 0.0,
        "income_change": 0.0,
        "expense_housing_change": 0.0,
        "expense_food_change": 0.0,
        "expense_transport_change": 0.0,
        "expense_utilities_change": 0.0,
        "expense_subscriptions_change": 0.0,
        "expense_insurance_change": 0.0,
        "expense_other_change": 0.0,
        "energy_change": 0,
        "motivation_change": 0,
        "social_change": 0,
        "knowledge_change": 0,
    }
    
    # Handle investment actions
    if action_type == "investment":
        investment_details = outcome.get("investment_details", {})
        principal = investment_details.get("principal", 0)
        asset_type = investment_details.get("asset_type", "")
        result_quality = investment_details.get("result_quality", "")
        
        if principal != 0 and asset_type and result_quality:
            try:
                # Calculate using MCP server
                mcp_client = await get_mcp_client()
                mcp_result = await mcp_client.calculate_investment_outcome(
                    principal=float(principal),
                    asset_type=asset_type,
                    result_quality=result_quality
                )
                
                # Apply calculated effects
                effects["money_change"] = mcp_result["money_change"]
                effects["investment_change"] = mcp_result["investment_change"]
                effects["passive_income_change"] = mcp_result["passive_income_change"]
                
            except (ValueError, KeyError) as e:
                # Log error but don't crash - fall back to no financial effects
                print(f"[WARNING] Investment calculation failed: {e}")
    
    # Handle expense changes
    elif action_type == "expense":
        expense_changes = outcome.get("expense_changes", {})
        for expense_key, change_value in expense_changes.items():
            if expense_key in effects and change_value is not None:
                effects[expense_key] = float(change_value)
    
    # Handle income changes
    if "income_change" in outcome and outcome["income_change"] is not None:
        effects["income_change"] = float(outcome["income_change"])
    
    # Handle debt changes
    if "debt_change" in outcome and outcome["debt_change"] is not None:
        effects["debt_change"] = float(outcome["debt_change"])
    
    # Apply life metrics
    life_metrics = outcome.get("life_metrics", {})
    for metric_key in ["energy_change", "motivation_change", "social_change", "knowledge_change"]:
        if metric_key in life_metrics and life_metrics[metric_key] is not None:
            effects[metric_key] = int(life_metrics[metric_key])
    
    return effects


async def validate_and_log_transaction(
    game_state_before: Dict,
    effects: Dict[str, float]
) -> bool:
    """
    Validate transaction maintains balance sheet integrity and log any issues.
    
    Args:
        game_state_before: GameState values before transaction
        effects: Calculated effects to apply
        
    Returns:
        True if valid, False if validation failed
    """
    money_before = game_state_before.get("money", 0)
    investments_before = game_state_before.get("investments", 0)
    money_change = effects.get("money_change", 0)
    investment_change = effects.get("investment_change", 0)
    
    # Skip validation if no financial changes
    if money_change == 0 and investment_change == 0:
        return True
    
    mcp_client = await get_mcp_client()
    validation_result = await mcp_client.validate_transaction(
        money_before=money_before,
        investments_before=investments_before,
        money_change=money_change,
        investment_change=investment_change
    )
    
    is_valid = validation_result['valid']
    message = validation_result['message']
    
    if not is_valid:
        print(f"[ERROR] Balance sheet validation failed: {message}")
        print(f"  Money: {money_before} -> {money_before + money_change}")
        print(f"  Investments: {investments_before} -> {investments_before + investment_change}")
        print(f"  Wealth change: {(money_before + money_change + investments_before + investment_change) - (money_before + investments_before)}")
        return False
    
    # Log successful validation
    print(f"[INFO] Transaction validated: {message}")
    return True


async def calculate_effects_from_llm(
    llm_response: Dict,
    game_state_before: Dict
) -> Optional[Dict[str, float]]:
    """
    Main entry point: Parse LLM response, calculate effects, validate.
    
    Args:
        llm_response: Response from LLM containing narrative and outcome
        game_state_before: Current GameState before applying effects
        
    Returns:
        Dictionary of effects to apply, or None if validation failed
    """
    # Parse and calculate
    effects = await parse_llm_outcome(llm_response)
    
    # Validate
    is_valid = await validate_and_log_transaction(game_state_before, effects)
    
    if not is_valid:
        # Return effects anyway but log the error
        # In production, you might want to reject the transaction
        print("[WARNING] Proceeding with invalid transaction - review logs")
    
    return effects


# Test function
async def test_financial_calculator():
    """Test the financial calculator middleware"""
    print("=== Financial Calculator Middleware Tests ===\n")
    
    # Test 1: Investment with gain
    print("Test 1: Parse LLM response for investment with gain")
    llm_response = {
        "narrative": "You invested €1000 in an index fund and it performed well.",
        "outcome": {
            "action_type": "investment",
            "investment_details": {
                "principal": 1000,
                "asset_type": "index_fund",
                "result_quality": "gain"
            },
            "life_metrics": {
                "energy_change": 0,
                "motivation_change": 10,
                "social_change": 0,
                "knowledge_change": 15
            }
        }
    }
    
    game_state_before = {
        "money": 5000,
        "investments": 10000
    }
    
    effects = await calculate_effects_from_llm(llm_response, game_state_before)
    print(f"  Money change: €{effects['money_change']}")
    print(f"  Investment change: €{effects['investment_change']}")
    print(f"  Passive income change: €{effects['passive_income_change']}/month")
    print(f"  Motivation change: {effects['motivation_change']}")
    print(f"  Knowledge change: {effects['knowledge_change']}\n")
    
    # Test 2: Expense change
    print("Test 2: Parse LLM response for expense reduction")
    llm_response = {
        "narrative": "You canceled your gym membership and streaming services.",
        "outcome": {
            "action_type": "expense",
            "expense_changes": {
                "expense_subscriptions_change": -65
            },
            "life_metrics": {
                "energy_change": -10,
                "motivation_change": -15,
                "social_change": 0,
                "knowledge_change": 5
            }
        }
    }
    
    effects = await calculate_effects_from_llm(llm_response, game_state_before)
    print(f"  Subscriptions change: €{effects['expense_subscriptions_change']}/month")
    print(f"  Energy change: {effects['energy_change']}")
    print(f"  Motivation change: {effects['motivation_change']}\n")
    
    # Test 3: Investment with major loss
    print("Test 3: Parse LLM response for risky investment with major loss")
    llm_response = {
        "narrative": "You invested €500 in crypto and it crashed hard.",
        "outcome": {
            "action_type": "investment",
            "investment_details": {
                "principal": 500,
                "asset_type": "crypto",
                "result_quality": "major_loss"
            },
            "life_metrics": {
                "energy_change": -15,
                "motivation_change": -25,
                "social_change": -5,
                "knowledge_change": 20
            }
        }
    }
    
    effects = await calculate_effects_from_llm(llm_response, game_state_before)
    print(f"  Money change: €{effects['money_change']}")
    print(f"  Investment change: €{effects['investment_change']}")
    print(f"  Net gain/loss: €{effects['investment_change'] - abs(effects['money_change'])}")
    print(f"  Motivation change: {effects['motivation_change']}\n")
    
    print("=== All middleware tests completed ===")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_financial_calculator())
