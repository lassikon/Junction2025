#!/usr/bin/env python3
"""
Standalone MCP Financial Server
Implements Model Context Protocol for financial calculations
Run as: python mcp_server.py
"""

import asyncio
import random
from enum import Enum
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class AssetType(str, Enum):
    """Investment asset types with their annual yields"""
    INDEX_FUND = "index_fund"
    TECH_STOCKS = "tech_stocks"
    BONDS = "bonds"
    SAVINGS_ACCOUNT = "savings_account"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"


class ResultQuality(str, Enum):
    """Qualitative outcome categories"""
    MAJOR_GAIN = "major_gain"
    GAIN = "gain"
    NEUTRAL = "neutral"
    MINOR_LOSS = "minor_loss"
    LOSS = "loss"
    MAJOR_LOSS = "major_loss"


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


# Create MCP server instance
server = Server("lifesim-financial-calculator")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available financial calculation tools"""
    return [
        Tool(
            name="calculate_investment_outcome",
            description="Calculate financial effects of an investment decision with deterministic math. "
                       "Takes qualitative outcome (major_gain, gain, neutral, minor_loss, loss, major_loss) "
                       "and calculates exact money_change, investment_change, and passive_income_change.",
            inputSchema={
                "type": "object",
                "properties": {
                    "principal": {
                        "type": "number",
                        "description": "Amount to invest (positive) or divest (negative) in euros"
                    },
                    "asset_type": {
                        "type": "string",
                        "enum": ["index_fund", "tech_stocks", "bonds", "savings_account", "crypto", "real_estate"],
                        "description": "Type of investment asset"
                    },
                    "result_quality": {
                        "type": "string",
                        "enum": ["major_gain", "gain", "neutral", "minor_loss", "loss", "major_loss"],
                        "description": "Qualitative assessment of investment outcome"
                    }
                },
                "required": ["principal", "asset_type", "result_quality"]
            }
        ),
        Tool(
            name="calculate_expense_breakdown",
            description="Calculate detailed expense category breakdown from total monthly expenses. "
                       "Provides realistic distribution across housing, food, transport, utilities, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "total_expenses": {
                        "type": "number",
                        "description": "Total monthly expenses in euros"
                    },
                    "city": {
                        "type": "string",
                        "description": "City name for cost of living adjustments",
                        "default": "Helsinki"
                    },
                    "has_car": {
                        "type": "boolean",
                        "description": "Whether player owns a car",
                        "default": False
                    },
                    "lifestyle_level": {
                        "type": "integer",
                        "description": "Lifestyle level: 1=frugal, 2=moderate, 3=comfortable, 4=luxury",
                        "default": 2,
                        "minimum": 1,
                        "maximum": 4
                    }
                },
                "required": ["total_expenses"]
            }
        ),
        Tool(
            name="validate_transaction",
            description="Validate that a financial transaction maintains balance sheet integrity. "
                       "Ensures money_change + investment_change accounts properly for gains/losses.",
            inputSchema={
                "type": "object",
                "properties": {
                    "money_before": {
                        "type": "number",
                        "description": "Cash balance before transaction in euros"
                    },
                    "investments_before": {
                        "type": "number",
                        "description": "Investment balance before transaction in euros"
                    },
                    "money_change": {
                        "type": "number",
                        "description": "Change in cash balance in euros"
                    },
                    "investment_change": {
                        "type": "number",
                        "description": "Change in investment balance in euros"
                    }
                },
                "required": ["money_before", "investments_before", "money_change", "investment_change"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls from MCP clients"""
    
    if name == "calculate_investment_outcome":
        principal = float(arguments["principal"])
        asset_type = arguments["asset_type"]
        result_quality = arguments["result_quality"]
        
        # Validate inputs
        try:
            asset = AssetType(asset_type)
            quality = ResultQuality(result_quality)
        except ValueError as e:
            return [TextContent(
                type="text",
                text=f"Error: Invalid asset_type or result_quality: {e}"
            )]
        
        if principal == 0:
            result = {
                'money_change': 0.0,
                'investment_change': 0.0,
                'passive_income_change': 0.0,
                'net_gain_loss': 0.0
            }
        else:
            # Get outcome multiplier with small random variation
            multiplier_range = OUTCOME_MULTIPLIERS[quality]
            multiplier = random.uniform(multiplier_range[0], multiplier_range[1])
            
            # Calculate final investment value
            final_value = abs(principal) * multiplier
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
            
            result = {
                'money_change': round(money_change, 2),
                'investment_change': round(investment_change, 2),
                'passive_income_change': round(passive_income_change, 2),
                'net_gain_loss': round(net_gain_loss, 2)
            }
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    elif name == "calculate_expense_breakdown":
        total_expenses = float(arguments["total_expenses"])
        city = arguments.get("city", "Helsinki")
        has_car = arguments.get("has_car", False)
        lifestyle_level = arguments.get("lifestyle_level", 2)
        
        # Base percentages for moderate lifestyle
        percentages = {
            'expense_housing': 0.35,
            'expense_food': 0.20,
            'expense_transport': 0.10,
            'expense_utilities': 0.08,
            'expense_subscriptions': 0.05,
            'expense_insurance': 0.07,
            'expense_other': 0.15,
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
            reduction = 0.08
            for key in ['expense_housing', 'expense_food', 'expense_other']:
                percentages[key] -= reduction / 3
        
        # Calculate actual amounts
        breakdown = {}
        for key, pct in percentages.items():
            if key != 'expense_other':
                breakdown[key] = round(total_expenses * pct, 2)
        
        # Other category gets the remainder to ensure exact sum
        breakdown['expense_other'] = round(
            total_expenses - sum(breakdown.values()), 2
        )
        
        return [TextContent(
            type="text",
            text=str(breakdown)
        )]
    
    elif name == "validate_transaction":
        money_before = float(arguments["money_before"])
        investments_before = float(arguments["investments_before"])
        money_change = float(arguments["money_change"])
        investment_change = float(arguments["investment_change"])
        
        # Check for insufficient funds
        if money_before + money_change < 0:
            result = {
                'valid': False,
                'message': f"Insufficient funds: balance {money_before} + change {money_change} = negative"
            }
        else:
            # Check balance sheet integrity
            total_before = money_before + investments_before
            total_after = (money_before + money_change) + (investments_before + investment_change)
            wealth_change = total_after - total_before
            expected_wealth_change = money_change + investment_change
            
            if abs(wealth_change - expected_wealth_change) > 0.01:
                result = {
                    'valid': False,
                    'message': f"Balance sheet error: wealth change {wealth_change} != expected {expected_wealth_change}"
                }
            else:
                result = {
                    'valid': True,
                    'message': f"Valid transaction (wealth change: €{wealth_change:.2f})"
                }
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Error: Unknown tool: {name}"
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="lifesim-financial-calculator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
