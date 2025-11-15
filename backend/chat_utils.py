"""
Chat utility functions for LifeSim chat system.

This module contains functions for:
- Chat session management
- Message retrieval and formatting
- Chat history summarization
- Context preparation for LLM
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import (
    ChatSession, ChatMessage, ChatSummary, ChatRole,
    PlayerProfile, GameState
)
from datetime import datetime
import uuid


def generate_chat_session_id() -> str:
    """
    Generate unique chat session ID using UUID4.
    
    Returns:
        Unique chat session identifier
    """
    return str(uuid.uuid4())


async def get_or_create_chat_session(
    session_id: str,
    profile_id: int,
    db_session: AsyncSession
) -> ChatSession:
    """
    Get existing chat session or create new one for a player.
    
    Args:
        session_id: Game session ID (from PlayerProfile.session_id)
        profile_id: Player profile ID
        db_session: Database session
        
    Returns:
        ChatSession object
    """
    # Try to find existing chat session for this profile
    result = await db_session.execute(
        select(ChatSession).where(ChatSession.profile_id == profile_id)
    )
    chat_session = result.scalar_one_or_none()
    
    if chat_session:
        return chat_session
    
    # Create new chat session
    chat_session_id = generate_chat_session_id()
    chat_session = ChatSession(
        chat_session_id=chat_session_id,
        profile_id=profile_id,
        message_count=0,
        last_summary_at=None
    )
    
    db_session.add(chat_session)
    await db_session.flush()  # Get the ID
    
    return chat_session


async def get_recent_chat_messages(
    chat_session_id: int,
    db_session: AsyncSession,
    limit: int = 20
) -> List[ChatMessage]:
    """
    Get recent chat messages, ordered chronologically (oldest first).
    
    Args:
        chat_session_id: Chat session database ID
        db_session: Database session
        limit: Maximum number of messages to retrieve
        
    Returns:
        List of ChatMessage objects, ordered oldest to newest
    """
    result = await db_session.execute(
        select(ChatMessage)
        .where(ChatMessage.chat_session_id == chat_session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    
    # Reverse to get chronological order (oldest first)
    return list(reversed(messages))


async def format_chat_history_for_llm(
    messages: List[ChatMessage]
) -> str:
    """
    Format chat history as conversation context for LLM prompts.
    
    Args:
        messages: List of ChatMessage objects
        
    Returns:
        Formatted string with conversation history
    """
    if not messages:
        return ""
    
    formatted_lines = ["=== CONVERSATION HISTORY ==="]
    
    for msg in messages:
        role_label = "User" if msg.role == ChatRole.USER else "Assistant"
        # Truncate very long messages for context efficiency
        content = msg.content
        if len(content) > 500:
            content = content[:497] + "..."
        
        formatted_lines.append(f"\n{role_label}: {content}")
    
    formatted_lines.append("\n" + "="*40)
    
    return "\n".join(formatted_lines)


async def get_latest_chat_summary(
    chat_session_id: int,
    db_session: AsyncSession
) -> Optional[ChatSummary]:
    """
    Get the most recent chat summary for a session.
    
    Args:
        chat_session_id: Chat session database ID
        db_session: Database session
        
    Returns:
        ChatSummary object or None
    """
    result = await db_session.execute(
        select(ChatSummary)
        .where(ChatSummary.chat_session_id == chat_session_id)
        .order_by(ChatSummary.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_chat_summary(
    messages: List[ChatMessage],
    game_state: GameState,
    profile: PlayerProfile,
    client
) -> str:
    """
    Create AI-generated summary of chat history using Gemini.
    
    Args:
        messages: List of ChatMessage objects to summarize
        game_state: Current game state
        profile: Player profile
        client: Gemini AI client
        
    Returns:
        Summary text
    """
    if not client:
        return create_fallback_summary(messages)
    
    try:
        # Format messages for summary
        conversation_text = []
        for msg in messages:
            role = "User" if msg.role == ChatRole.USER else "Assistant"
            conversation_text.append(f"{role}: {msg.content}")
        
        conversation = "\n".join(conversation_text)
        
        prompt = f"""Summarize this conversation between a financial literacy game player and their AI assistant.
Focus on:
- Key financial topics discussed
- Questions asked by the player
- Advice or guidance provided
- Player's current financial situation (Age: {game_state.current_age}, FI Score: {game_state.fi_score}%)

Keep the summary concise (2-3 sentences).

CONVERSATION:
{conversation}

SUMMARY:"""
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"⚠️ AI summary failed: {e}")
        return create_fallback_summary(messages)


def create_fallback_summary(messages: List[ChatMessage]) -> str:
    """
    Create simple rule-based summary when AI is unavailable.
    
    Args:
        messages: List of ChatMessage objects
        
    Returns:
        Simple summary text
    """
    user_messages = [m for m in messages if m.role == ChatRole.USER]
    assistant_messages = [m for m in messages if m.role == ChatRole.ASSISTANT]
    
    return (
        f"Conversation history: {len(messages)} messages "
        f"({len(user_messages)} from player, {len(assistant_messages)} responses). "
        f"Discussion about financial topics and game guidance."
    )


async def get_chat_context_for_llm(
    chat_session_id: int,
    game_state: GameState,
    profile: PlayerProfile,
    db_session: AsyncSession,
    max_recent: int = 5
) -> str:
    """
    Get comprehensive chat context for LLM, combining summary and recent messages.
    
    Args:
        chat_session_id: Chat session database ID
        game_state: Current game state
        profile: Player profile
        db_session: Database session
        max_recent: Maximum number of recent messages to include
        
    Returns:
        Formatted context string
    """
    # Get chat session
    result = await db_session.execute(
        select(ChatSession).where(ChatSession.id == chat_session_id)
    )
    chat_session = result.scalar_one_or_none()
    
    if not chat_session:
        return ""
    
    context_parts = []
    
    # If more than 10 messages, include summary
    if chat_session.message_count > 10:
        summary = await get_latest_chat_summary(chat_session_id, db_session)
        if summary:
            context_parts.append("=== CONVERSATION SUMMARY ===")
            context_parts.append(summary.summary_text)
            context_parts.append("")
    
    # Get recent messages
    recent_messages = await get_recent_chat_messages(
        chat_session_id,
        db_session,
        limit=max_recent
    )
    
    if recent_messages:
        formatted_history = await format_chat_history_for_llm(recent_messages)
        context_parts.append(formatted_history)
    
    return "\n".join(context_parts)


async def save_chat_message(
    chat_session: ChatSession,
    role: ChatRole,
    content: str,
    db_session: AsyncSession,
    message_metadata: dict = None
) -> ChatMessage:
    """
    Save a chat message to the database.
    
    Args:
        chat_session: ChatSession object
        role: Message role (user or assistant)
        content: Message content
        db_session: Database session
        message_metadata: Optional metadata dictionary
        
    Returns:
        Saved ChatMessage object
    """
    message = ChatMessage(
        chat_session_id=chat_session.id,
        role=role,
        content=content,
        message_metadata=message_metadata or {}
    )
    
    db_session.add(message)
    
    # Update session metadata
    chat_session.message_count += 1
    chat_session.updated_at = datetime.utcnow()
    
    await db_session.flush()
    
    return message


async def should_create_summary(chat_session: ChatSession) -> bool:
    """
    Check if a new summary should be created.
    Creates summary every 10 messages.
    
    Args:
        chat_session: ChatSession object
        
    Returns:
        True if summary should be created
    """
    if chat_session.message_count < 10:
        return False
    
    # Create summary every 10 messages
    if chat_session.last_summary_at is None:
        return chat_session.message_count >= 10
    
    return chat_session.message_count - chat_session.last_summary_at >= 10


async def store_chat_summary(
    chat_session: ChatSession,
    summary_text: str,
    message_range_start: int,
    message_range_end: int,
    db_session: AsyncSession
) -> ChatSummary:
    """
    Store a chat summary in the database.
    
    Args:
        chat_session: ChatSession object
        summary_text: Summary content
        message_range_start: Starting message number
        message_range_end: Ending message number
        db_session: Database session
        
    Returns:
        Saved ChatSummary object
    """
    summary = ChatSummary(
        chat_session_id=chat_session.id,
        summary_text=summary_text,
        messages_included=message_range_end - message_range_start + 1,
        message_range_start=message_range_start,
        message_range_end=message_range_end
    )
    
    db_session.add(summary)
    
    # Update last summary marker
    chat_session.last_summary_at = message_range_end
    
    await db_session.flush()
    
    return summary
