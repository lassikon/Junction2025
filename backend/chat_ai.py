"""
AI chat response generation for LifeSim.

This module handles:
- Game-aware chat responses
- Context integration (game state, chat history, decisions)
- Financial guidance tailored to player's situation
"""

from typing import Optional
from google import genai
from sqlalchemy.ext.asyncio import AsyncSession
from models import ChatSession, GameState, PlayerProfile
from chat_utils import get_chat_context_for_llm
import os


def get_ai_client():
    """
    Get Gemini client from environment.
    
    Returns:
        Gemini Client or None if API key not configured
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


async def generate_chat_response(
    user_message: str,
    chat_session: ChatSession,
    game_state: GameState,
    profile: PlayerProfile,
    db_session: AsyncSession,
    client: Optional[genai.Client] = None
) -> str:
    """
    Generate game-aware chat response using Gemini AI.
    
    This function creates responses that are aware of:
    - Player's current game state (age, FI score, finances)
    - Player's profile (education, risk attitude, aspirations)
    - Recent chat history
    - Recent game decisions (if available)
    
    Args:
        user_message: The user's message
        chat_session: Current chat session
        game_state: Player's game state
        profile: Player's profile
        db_session: Database session
        client: Gemini AI client (optional)
        
    Returns:
        AI-generated response text
    """
    # Get or create client
    if client is None:
        client = get_ai_client()
    
    # Fallback if no client available
    if client is None:
        return get_fallback_response(user_message, game_state, profile)
    
    try:
        # Build comprehensive context
        context = await build_chat_context(
            chat_session=chat_session,
            game_state=game_state,
            profile=profile,
            db_session=db_session
        )
        
        # Build prompt
        prompt = build_chat_prompt(
            user_message=user_message,
            context=context,
            game_state=game_state,
            profile=profile
        )
        
        # Log the request
        print("\n" + "="*80)
        print("💬 GEMINI API CALL - Chat Response")
        print("="*80)
        print("USER MESSAGE:", user_message)
        print("-"*80)
        print("CONTEXT LENGTH:", len(context))
        print("-"*80)
        
        # Generate response
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        response_text = response.text.strip()
        
        print("RESPONSE:", response_text[:200] + "..." if len(response_text) > 200 else response_text)
        print("="*80 + "\n")
        
        return response_text
        
    except Exception as e:
        print(f"❌ Chat AI generation failed: {e}")
        import traceback
        traceback.print_exc()
        return get_fallback_response(user_message, game_state, profile)


async def build_chat_context(
    chat_session: ChatSession,
    game_state: GameState,
    profile: PlayerProfile,
    db_session: AsyncSession
) -> str:
    """
    Build comprehensive context for chat AI including:
    - Chat history (with summary if needed)
    - Game state information
    - Recent decisions (if available)
    
    Args:
        chat_session: Current chat session
        game_state: Player's game state
        profile: Player's profile
        db_session: Database session
        
    Returns:
        Formatted context string
    """
    context_parts = []
    
    # Get chat history context
    chat_context = await get_chat_context_for_llm(
        chat_session_id=chat_session.id,
        game_state=game_state,
        profile=profile,
        db_session=db_session,
        max_recent=5
    )
    
    if chat_context:
        context_parts.append(chat_context)
    
    # Get recent decisions context (if available)
    try:
        from utils import get_decision_context_for_llm
        
        decision_context = await get_decision_context_for_llm(
            profile_id=profile.id,
            db_session=db_session,
            current_age=game_state.current_age,
            current_fi_score=game_state.fi_score,
            max_recent=3
        )
        
        if decision_context:
            context_parts.append("\n" + decision_context)
            
    except Exception as e:
        print(f"⚠️ Could not retrieve decision context: {e}")
    
    return "\n\n".join(context_parts)


def build_chat_prompt(
    user_message: str,
    context: str,
    game_state: GameState,
    profile: PlayerProfile
) -> str:
    """
    Build the complete prompt for chat AI.
    
    Args:
        user_message: User's message
        context: Conversation and game context
        game_state: Player's game state
        profile: Player's profile
        
    Returns:
        Complete prompt string
    """
    # Calculate financial metrics
    net_worth = game_state.money + game_state.investments - game_state.debts
    savings_rate = 0
    if game_state.monthly_income > 0:
        net_monthly = game_state.monthly_income - game_state.monthly_expenses
        savings_rate = (net_monthly / game_state.monthly_income) * 100
    
    prompt = f"""You are a helpful financial literacy assistant in the LifeSim game. Your role is to:
- Provide clear, actionable financial advice
- Explain financial concepts in simple terms
- Be encouraging and supportive
- Reference the player's current situation
- Keep responses VERY SHORT: maximum 3-4 sentences or 60 words
- Get straight to the point - no lengthy explanations

PLAYER'S CURRENT SITUATION:
- Name: {profile.player_name}
- Age: {game_state.current_age}
- Education: {profile.education_path.value}
- Risk Attitude: {profile.risk_attitude.value}

FINANCIAL METRICS:
- FI Score: {game_state.fi_score:.1f}% (target: 100%)
- Net Worth: €{net_worth:,.0f}
- Cash: €{game_state.money:,.0f}
- Investments: €{game_state.investments:,.0f}
- Debts: €{game_state.debts:,.0f}
- Monthly Income: €{game_state.monthly_income:,.0f}
- Monthly Expenses: €{game_state.monthly_expenses:,.0f}
- Savings Rate: {savings_rate:.1f}%

LIFE METRICS:
- Energy: {game_state.energy}/100
- Motivation: {game_state.motivation}/100
- Social Life: {game_state.social_life}/100
- Financial Knowledge: {game_state.financial_knowledge}/100

{context}

USER'S QUESTION:
{user_message}

RESPONSE (be helpful, specific, encouraging, and BRIEF - max 3-4 sentences):"""
    
    return prompt


def get_fallback_response(
    user_message: str,
    game_state: GameState,
    profile: PlayerProfile
) -> str:
    """
    Generate fallback response when AI is unavailable.
    
    Args:
        user_message: User's message
        game_state: Player's game state
        profile: Player's profile
        
    Returns:
        Simple fallback response
    """
    # Detect question type and provide basic response
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ["fi score", "financial independence", "retire"]):
        return (
            f"Your Financial Independence (FI) Score is currently {game_state.fi_score:.1f}%. "
            f"This measures how close you are to financial independence, where your passive income "
            f"covers your living expenses. Keep building investments to increase passive income!"
        )
    
    elif any(word in message_lower for word in ["invest", "stock", "portfolio"]):
        return (
            f"You currently have €{game_state.investments:,.0f} in investments generating "
            f"€{game_state.passive_income:,.0f} monthly passive income. Regular investing is key to "
            f"building wealth over time. Consider your risk tolerance ({profile.risk_attitude.value}) "
            f"when choosing investments."
        )
    
    elif any(word in message_lower for word in ["save", "saving", "money"]):
        net_monthly = game_state.monthly_income - game_state.monthly_expenses
        return (
            f"You currently have €{game_state.money:,.0f} in cash. With income of "
            f"€{game_state.monthly_income:,.0f} and expenses of €{game_state.monthly_expenses:,.0f}, "
            f"you're saving €{net_monthly:,.0f} per month. Try to save at least 20% of your income!"
        )
    
    elif any(word in message_lower for word in ["debt", "loan", "owe"]):
        if game_state.debts > 0:
            return (
                f"You currently have €{game_state.debts:,.0f} in debt. Paying down high-interest "
                f"debt should be a priority as it reduces your net worth and financial flexibility."
            )
        else:
            return (
                "Great news - you have no debt! This gives you financial flexibility. "
                "Now focus on building your emergency fund and investments."
            )
    
    else:
        return (
            f"I'm here to help with your financial journey! You're {game_state.current_age} years old "
            f"with a FI Score of {game_state.fi_score:.1f}%. Feel free to ask about investments, "
            f"savings, debt management, or any financial concepts from the game."
        )
