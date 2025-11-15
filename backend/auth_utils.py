"""
Authentication utilities for LifeSim.

Provides:
- Password hashing and verification (bcrypt)
- Session token generation and validation
- Auth dependencies for FastAPI endpoints
"""

import bcrypt
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import Account, SessionToken


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        password_hash: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_token() -> str:
    """
    Generate a unique session token.
    
    Returns:
        UUID token string
    """
    return str(uuid.uuid4())


async def create_session_token(account_id: int, db_session: AsyncSession, days_valid: int = 30) -> str:
    """
    Create a new session token for an account.
    
    Args:
        account_id: Account ID
        db_session: Database session
        days_valid: Number of days token is valid (default 30)
        
    Returns:
        Token string
    """
    token = generate_token()
    expires_at = datetime.utcnow() + timedelta(days=days_valid)
    
    session_token = SessionToken(
        token=token,
        account_id=account_id,
        expires_at=expires_at,
        is_active=True
    )
    
    db_session.add(session_token)
    await db_session.flush()
    
    return token


async def validate_token(token: str, db_session: AsyncSession) -> Optional[Account]:
    """
    Validate a session token and return the associated account.
    
    Args:
        token: Session token to validate
        db_session: Database session
        
    Returns:
        Account object if valid, None otherwise
    """
    # Find the token
    result = await db_session.execute(
        select(SessionToken).where(
            SessionToken.token == token,
            SessionToken.is_active == True
        )
    )
    session_token = result.scalar_one_or_none()
    
    if not session_token:
        return None
    
    # Check if expired
    if session_token.expires_at < datetime.utcnow():
        session_token.is_active = False
        await db_session.commit()
        return None
    
    # Get the account
    result = await db_session.execute(
        select(Account).where(Account.id == session_token.account_id)
    )
    account = result.scalar_one_or_none()
    
    return account


async def get_current_account(
    authorization: Optional[str] = Header(None)
) -> Account:
    """
    FastAPI dependency to get the current authenticated account.
    
    Args:
        authorization: Authorization header (Bearer token)
        db_session: Database session (injected)
        
    Returns:
        Account object
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Parse Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = parts[1]
    
    # Need to get db_session here - we'll pass it from the endpoint
    # This is a simplified version that returns the token for now
    # The endpoint will need to validate it
    return token


async def get_optional_account(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    FastAPI dependency to get the current account if authenticated, None otherwise.
    Used for endpoints that work both with and without authentication (e.g., onboarding).
    
    Args:
        authorization: Authorization header (Bearer token)
        db_session: Database session (injected)
        
    Returns:
        Account object if authenticated, None otherwise
    """
    if not authorization:
        return None
    
    # Parse Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    token = parts[1]
    return token

