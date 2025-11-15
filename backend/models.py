"""
Database models for LifeSim: Financial Independence Quest

This module defines the SQLModel models for:
- Player profile and state
- Game sessions
- Decision history
- Leaderboard entries
- Chat sessions and messages
"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, JSON, Column
from enum import Enum


class RiskAttitude(str, Enum):
    """Player's attitude towards financial risk"""
    RISK_AVERSE = "risk_averse"
    BALANCED = "balanced"
    RISK_SEEKING = "risk_seeking"


class EducationPath(str, Enum):
    """Player's education path"""
    VOCATIONAL = "vocational"
    UNIVERSITY = "university"
    HIGH_SCHOOL = "high_school"
    WORKING = "working"


class GameStatus(str, Enum):
    """Current status of a game session"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ChatRole(str, Enum):
    """Role of chat message sender"""
    USER = "user"
    ASSISTANT = "assistant"


# Player Profile Model
class PlayerProfile(SQLModel, table=True):
    """
    Stores the player's initial profile data from onboarding.
    This is mostly static and set at the beginning of each game session.
    """
    __tablename__ = "player_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Unique identifier for this game session
    session_id: str = Field(index=True, unique=True)

    # Player identification
    player_name: str = Field(max_length=100)

    # Onboarding data
    age: int = Field(ge=15, le=35)
    city: str = Field(default="Helsinki")
    education_path: EducationPath
    risk_attitude: RiskAttitude

    # Starting conditions
    starting_savings: float = Field(default=0.0, ge=0)
    starting_debt: float = Field(default=0.0, ge=0)

    # Aspirations (stored as JSON for flexibility)
    aspirations: dict = Field(default={}, sa_column=Column(JSON))
    # Example: {"own_car": True, "travel": True, "own_pet": False}

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    game_state: Optional["GameState"] = Relationship(
        back_populates="player_profile")
    decisions: List["DecisionHistory"] = Relationship(
        back_populates="player_profile")
    chat_sessions: List["ChatSession"] = Relationship(
        back_populates="player_profile")


# Game State Model
class GameState(SQLModel, table=True):
    """
    Stores the current state of a player's game session.
    This is updated after each decision.
    """
    __tablename__ = "game_states"

    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="player_profiles.id", unique=True)

    # Game progress
    # Which decision/event the player is on
    current_step: int = Field(default=0)
    game_status: GameStatus = Field(default=GameStatus.ACTIVE)

    # Time tracking
    current_age: int = Field(default=25)  # Updates as time passes
    years_passed: float = Field(default=0.0)  # Total game time in years

    # Financial metrics
    money: float = Field(default=0.0)  # Current cash/savings
    monthly_income: float = Field(default=0.0)
    monthly_expenses: float = Field(default=0.0)
    investments: float = Field(default=0.0)  # Value of investments
    passive_income: float = Field(default=0.0)  # Income from investments
    debts: float = Field(default=0.0)

    # FI Score: (Passive income / Monthly cost of living) × 100%
    fi_score: float = Field(default=0.0, ge=0, le=100)

    # Life metrics (0-100 scale)
    energy: int = Field(default=70, ge=0, le=100)
    motivation: int = Field(default=70, ge=0, le=100)
    social_life: int = Field(default=70, ge=0, le=100)
    financial_knowledge: int = Field(default=30, ge=0, le=100)

    # Assets (stored as JSON for flexibility)
    assets: dict = Field(default={}, sa_column=Column(JSON))
    # Example: {"car": {"type": "used_sedan", "value": 5000}, "pet": {"type": "cat"}}

    # Risk factors for curveballs
    risk_factors: dict = Field(default={}, sa_column=Column(JSON))
    # Example: {"has_car": True, "has_pet": True, "has_rental": True}

    # Timestamps
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    player_profile: PlayerProfile = Relationship(back_populates="game_state")


# Decision History Model
class DecisionHistory(SQLModel, table=True):
    """
    Stores each decision made by the player for replay and analysis.
    """
    __tablename__ = "decision_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="player_profiles.id", index=True)

    # Decision details
    step_number: int
    event_type: str  # e.g., "paycheck", "unexpected_expense", "curveball"
    narrative: str  # The story presented to the player

    # Decision made
    options_presented: List[str] = Field(default=[], sa_column=Column(JSON))
    chosen_option: str

    # State before decision
    money_before: float
    fi_score_before: float
    energy_before: int
    motivation_before: int
    social_before: int

    # State after decision
    money_after: float
    fi_score_after: float
    energy_after: int
    motivation_after: int
    social_after: int

    # AI-generated consequence narrative
    consequence_narrative: str

    # Learning moment (if any)
    learning_moment: Optional[str] = None

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    player_profile: PlayerProfile = Relationship(back_populates="decisions")


# Leaderboard Model
class LeaderboardEntry(SQLModel, table=True):
    """
    Stores completed game results for the leaderboard.
    """
    __tablename__ = "leaderboard"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)

    # Player info
    player_name: str
    age: int
    education_path: EducationPath

    # Final scores
    final_fi_score: float = Field(ge=0, le=100)
    final_money: float
    final_energy: int = Field(ge=0, le=100)
    final_motivation: int = Field(ge=0, le=100)
    final_social: int = Field(ge=0, le=100)
    final_knowledge: int = Field(ge=0, le=100)

    # Overall balance score (average of energy, motivation, social)
    balance_score: float = Field(ge=0, le=100)

    # Game stats
    steps_completed: int
    total_income_earned: float
    total_spent: float
    best_decision: Optional[str] = None
    worst_decision: Optional[str] = None

    # Timestamp
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    # Index for leaderboard queries
    class Config:
        arbitrary_types_allowed = True


# Chat Models
class ChatSession(SQLModel, table=True):
    """
    Stores chat session data for each player.
    Each player can have one active chat session per game session.
    """
    __tablename__ = "chat_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Unique identifier for this chat session (UUID)
    chat_session_id: str = Field(index=True, unique=True)
    # Link to player profile
    profile_id: int = Field(foreign_key="player_profiles.id", index=True)

    # Session metadata
    message_count: int = Field(default=0)
    last_summary_at: Optional[int] = None  # Message count when last summarized

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    player_profile: PlayerProfile = Relationship(back_populates="chat_sessions")
    messages: List["ChatMessage"] = Relationship(
        back_populates="chat_session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    summaries: List["ChatSummary"] = Relationship(
        back_populates="chat_session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class ChatMessage(SQLModel, table=True):
    """
    Stores individual chat messages in a conversation.
    """
    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Link to chat session
    chat_session_id: int = Field(foreign_key="chat_sessions.id", index=True)

    # Message content
    role: ChatRole
    content: str

    # Optional metadata (e.g., model used, token count, etc.)
    message_metadata: dict = Field(default={}, sa_column=Column(JSON))

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    chat_session: ChatSession = Relationship(back_populates="messages")


class ChatSummary(SQLModel, table=True):
    """
    Stores AI-generated summaries of chat history.
    Created when message count exceeds threshold (every 10 messages).
    """
    __tablename__ = "chat_summaries"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Link to chat session
    chat_session_id: int = Field(foreign_key="chat_sessions.id", index=True)

    # Summary content
    summary_text: str
    # Number of messages included in this summary
    messages_included: int
    # Message count range (e.g., messages 1-10)
    message_range_start: int
    message_range_end: int

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    chat_session: ChatSession = Relationship(back_populates="summaries")


# Pydantic models for API requests/responses

class OnboardingRequest(SQLModel):
    """Request model for the onboarding endpoint"""
    player_name: str = Field(max_length=100)
    age: int = Field(ge=15, le=35)
    city: str = "Helsinki"
    education_path: EducationPath
    risk_attitude: RiskAttitude
    monthly_income: float = Field(gt=0)
    monthly_expenses: float = Field(ge=0)
    starting_savings: float = Field(default=0.0, ge=0)
    starting_debt: float = Field(default=0.0, ge=0)
    aspirations: dict = {}


class GameStateResponse(SQLModel):
    """Response model with current game state"""
    session_id: str
    current_step: int
    current_age: int  # Player's current age
    years_passed: float  # Time elapsed in game

    # Financial metrics
    money: float
    monthly_income: float
    monthly_expenses: float
    investments: float
    passive_income: float
    debts: float
    fi_score: float

    # Life metrics
    energy: int
    motivation: int
    social_life: int
    financial_knowledge: int

    # Assets and status
    assets: dict
    game_status: GameStatus


class OnboardingResponse(SQLModel):
    """Response model for onboarding with initial narrative"""
    game_state: GameStateResponse
    initial_narrative: str
    initial_options: List[str]


class DecisionRequest(SQLModel):
    """Request model for making a decision"""
    session_id: str
    chosen_option: str
    # Index of the chosen option for reliable matching
    option_index: Optional[int] = None


class DecisionResponse(SQLModel):
    """Response model after making a decision"""
    consequence_narrative: str
    updated_state: GameStateResponse
    next_narrative: str
    next_options: List[str]
    learning_moment: Optional[str] = None


class LeaderboardResponse(SQLModel):
    """Response model for leaderboard data"""
    rank: int
    player_name: str
    final_fi_score: float
    balance_score: float
    age: int
    education_path: EducationPath
    completed_at: datetime


# Chat API Models
class ChatRequest(SQLModel):
    """Request model for sending a chat message"""
    session_id: str
    message: str
    model: Optional[str] = "gemini-2.0-flash-exp"


class ChatResponse(SQLModel):
    """Response model for chat message"""
    response: str
    session_id: str
    chat_session_id: str
    message_id: int
    model: str


class ChatMessageResponse(SQLModel):
    """Response model for individual chat message"""
    id: int
    role: ChatRole
    content: str
    created_at: datetime


class ChatHistoryResponse(SQLModel):
    """Response model for chat history with pagination"""
    session_id: str
    chat_session_id: str
    messages: List[ChatMessageResponse]
    summary: Optional[str] = None
    total_count: int
    current_page: int
    page_size: int
    has_more: bool
