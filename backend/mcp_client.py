"""
MCP Client for LifeSim Financial Calculator
Connects to the standalone MCP server for financial calculations
"""

import asyncio
import json
import os
from typing import Dict, Optional, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPFinancialClient:
    """Client for communicating with MCP financial calculator server"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack: Optional[AsyncExitStack] = None
        self._connected = False
    
    async def connect(self):
        """Connect to the MCP server"""
        if self._connected:
            return
        
        # Get absolute path to mcp_server.py
        server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
        
        server_params = StdioServerParameters(
            command="python3",
            args=[server_path],
            env=None
        )
        
        self.exit_stack = AsyncExitStack()
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        
        await self.session.initialize()
        self._connected = True
        print("[MCP] Connected to financial calculator server")
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.exit_stack:
            await self.exit_stack.aclose()
            self._connected = False
            print("[MCP] Disconnected from financial calculator server")
    
    async def calculate_investment_outcome(
        self,
        principal: float,
        asset_type: str,
        result_quality: str
    ) -> Dict[str, float]:
        """
        Call the calculate_investment_outcome tool on MCP server
        
        Returns:
            {
                'money_change': float,
                'investment_change': float,
                'passive_income_change': float,
                'net_gain_loss': float
            }
        """
        if not self._connected:
            await self.connect()
        
        result = await self.session.call_tool(
            "calculate_investment_outcome",
            arguments={
                "principal": principal,
                "asset_type": asset_type,
                "result_quality": result_quality
            }
        )
        
        # Parse the text response (it's a string representation of dict)
        result_text = result.content[0].text
        return eval(result_text)  # Safe here since we control the server output
    
    async def calculate_expense_breakdown(
        self,
        total_expenses: float,
        city: str = "Helsinki",
        has_car: bool = False,
        lifestyle_level: int = 2
    ) -> Dict[str, float]:
        """
        Call the calculate_expense_breakdown tool on MCP server
        
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
        if not self._connected:
            await self.connect()
        
        result = await self.session.call_tool(
            "calculate_expense_breakdown",
            arguments={
                "total_expenses": total_expenses,
                "city": city,
                "has_car": has_car,
                "lifestyle_level": lifestyle_level
            }
        )
        
        result_text = result.content[0].text
        return eval(result_text)
    
    async def validate_transaction(
        self,
        money_before: float,
        investments_before: float,
        money_change: float,
        investment_change: float
    ) -> Dict[str, Any]:
        """
        Call the validate_transaction tool on MCP server
        
        Returns:
            {
                'valid': bool,
                'message': str
            }
        """
        if not self._connected:
            await self.connect()
        
        result = await self.session.call_tool(
            "validate_transaction",
            arguments={
                "money_before": money_before,
                "investments_before": investments_before,
                "money_change": money_change,
                "investment_change": investment_change
            }
        )
        
        result_text = result.content[0].text
        return eval(result_text)


# Global MCP client instance
_mcp_client: Optional[MCPFinancialClient] = None


async def get_mcp_client() -> MCPFinancialClient:
    """Get or create the global MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPFinancialClient()
        await _mcp_client.connect()
    return _mcp_client


async def close_mcp_client():
    """Close the global MCP client"""
    global _mcp_client
    if _mcp_client:
        await _mcp_client.disconnect()
        _mcp_client = None


# Test function
async def test_mcp_client():
    """Test the MCP client"""
    print("=== MCP Client Tests ===\n")
    
    client = await get_mcp_client()
    
    # Test 1: Investment calculation
    print("Test 1: Calculate investment with gain")
    result = await client.calculate_investment_outcome(
        principal=1000.0,
        asset_type="index_fund",
        result_quality="gain"
    )
    print(f"  Money change: €{result['money_change']}")
    print(f"  Investment change: €{result['investment_change']}")
    print(f"  Passive income change: €{result['passive_income_change']}/month")
    print(f"  Net gain/loss: €{result['net_gain_loss']}\n")
    
    # Test 2: Expense breakdown
    print("Test 2: Calculate expense breakdown")
    result = await client.calculate_expense_breakdown(
        total_expenses=1500.0,
        has_car=True,
        lifestyle_level=2
    )
    print(f"  Housing: €{result['expense_housing']}")
    print(f"  Food: €{result['expense_food']}")
    print(f"  Transport: €{result['expense_transport']}")
    print(f"  Total: €{sum(result.values())}\n")
    
    # Test 3: Validation
    print("Test 3: Validate transaction")
    result = await client.validate_transaction(
        money_before=5000.0,
        investments_before=10000.0,
        money_change=-1000.0,
        investment_change=1100.0
    )
    print(f"  Valid: {result['valid']}")
    print(f"  Message: {result['message']}\n")
    
    await close_mcp_client()
    print("=== All tests completed ===")


if __name__ == "__main__":
    asyncio.run(test_mcp_client())
