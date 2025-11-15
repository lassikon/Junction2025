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


# Account Model
class Account(SQLModel, table=True):
    """
    User accounts for persistent identity across game sessions.
    Users can register and link multiple games to their account.
    """
    __tablename__ = "accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    password_hash: str  # Bcrypt hashed password
    display_name: str = Field(max_length=100)

    # Account metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # Onboarding completion status
    has_completed_onboarding: bool = Field(default=False)

    # Persistent onboarding data (saved so they don't re-do onboarding each game)
    default_age: Optional[int] = None
    default_city: Optional[str] = None
    default_education_path: Optional[str] = None  # Store as string to avoid enum issues
    default_risk_attitude: Optional[str] = None  # Store as string to avoid enum issues
    default_monthly_income: Optional[float] = None
    default_monthly_expenses: Optional[float] = None
    default_starting_savings: Optional[float] = None
    default_starting_debt: Optional[float] = None
    default_aspirations: dict = Field(default={}, sa_column=Column(JSON))

    # Relationships
    game_sessions: List["PlayerProfile"] = Relationship(back_populates="account")
    session_tokens: List["SessionToken"] = Relationship(back_populates="account")


# Session Token Model
class SessionToken(SQLModel, table=True):
    """
    Session tokens for authentication.
    Simple session-based auth (easier for hackathon than JWT).
    """
    __tablename__ = "session_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(index=True, unique=True)
    account_id: int = Field(foreign_key="accounts.id", index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # Token expiration
    is_active: bool = Field(default=True)

    # Relationships
    account: Account = Relationship(back_populates="session_tokens")


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

    # Account linkage (nullable for test mode/guest players)
    account_id: Optional[int] = Field(default=None, foreign_key="accounts.id", index=True)
    is_test_mode: bool = Field(default=False)  # True if playing as guest (not saved to leaderboard)

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
    account: Optional["Account"] = Relationship(back_populates="game_sessions")
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
    months_passed: int = Field(default=0)  # Total months in game
    # 1=early, 2=mid, 3=late month
    month_phase: int = Field(default=1, ge=1, le=3)

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


# Transaction Log Model
class TransactionLog(SQLModel, table=True):
    """
    Stores detailed financial transaction logs for each decision.
    Tracks all money movements for player transparency and analysis.
    """
    __tablename__ = "transaction_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="player_profiles.id", index=True)

    # Transaction context
    step_number: int
    event_type: str
    chosen_option: str

    # Transaction details (amounts in euros)
    # Positive values = gains, Negative values = losses
    cash_change: float = Field(default=0.0)
    investment_change: float = Field(default=0.0)
    debt_change: float = Field(default=0.0)

    # Monthly recurring changes
    monthly_income_change: float = Field(default=0.0)
    monthly_expense_change: float = Field(default=0.0)
    passive_income_change: float = Field(default=0.0)

    # Balances after transaction
    cash_balance: float
    investment_balance: float
    debt_balance: float
    monthly_income_total: float
    monthly_expense_total: float
    passive_income_total: float

    # Description of the transaction
    description: str

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Leaderboard Model
class LeaderboardEntry(SQLModel, table=True):
    """
    Stores completed game results for the leaderboard.
    """
    __tablename__ = "leaderboard"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)

    # Account linkage (nullable for test mode)
    account_id: Optional[int] = Field(default=None, foreign_key="accounts.id", index=True)
    is_test_mode: bool = Field(default=False)  # Don't show test mode plays on leaderboard

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
    months_passed: int = 0  # Total months elapsed
    month_phase: int = 1  # Current phase within month (1, 2, or 3)

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
    transaction_summary: Optional["TransactionSummary"] = None
    monthly_cash_flow: Optional["MonthlyCashFlowSummary"] = None
    life_metrics_changes: Optional["LifeMetricsChanges"] = None


class MonthlyCashFlowSummary(SQLModel):
    """Summary of monthly income/expense cash flow for the turn"""
    applied: bool = True  # Whether cash flow was applied this turn (only true for phase 1)
    income_received: float = 0.0
    expenses_paid: float = 0.0
    net_change: float = 0.0
    debt_from_deficit: float = 0.0
    month_name: str = ""
    month_phase: int = 1  # 1, 2, or 3
    month_phase_name: str = "Early"  # Early, Mid, Late


class LifeMetricsChanges(SQLModel):
    """Summary of life metrics changes from a decision"""
    energy_change: int = 0
    motivation_change: int = 0
    social_change: int = 0
    knowledge_change: int = 0


class TransactionSummary(SQLModel):
    """Summary of financial changes from a decision"""
    # One-time changes
    cash_change: float
    investment_change: float
    debt_change: float

    # Monthly recurring changes
    monthly_income_change: float
    monthly_expense_change: float
    passive_income_change: float

    # New balances
    cash_balance: float
    investment_balance: float
    debt_balance: float
    monthly_income_total: float
    monthly_expense_total: float
    passive_income_total: float

    # Human-readable description
    description: str

    # Timestamp for when this occurred
    timestamp: Optional[str] = None


class TransactionLogResponse(SQLModel):
    """Response model for transaction log entry"""
    step_number: int
    event_type: str
    chosen_option: str
    cash_change: float
    investment_change: float
    debt_change: float
    monthly_income_change: float
    monthly_expense_change: float
    passive_income_change: float
    description: str
    created_at: datetime


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


# Authentication API Models
class RegisterRequest(SQLModel):
    """Request model for account registration"""
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)
    display_name: str = Field(min_length=1, max_length=100)


class LoginRequest(SQLModel):
    """Request model for login"""
    username: str
    password: str


class AuthResponse(SQLModel):
    """Response model for authentication (login/register)"""
    token: str
    account_id: int
    username: str
    display_name: str
    has_completed_onboarding: bool


class AccountProfileResponse(SQLModel):
    """Response model for account profile"""
    account_id: int
    username: str
    display_name: str
    created_at: datetime
    has_completed_onboarding: bool
    default_age: Optional[int] = None
    default_city: Optional[str] = None
    default_education_path: Optional[str] = None
    default_risk_attitude: Optional[str] = None
    default_monthly_income: Optional[float] = None
    default_monthly_expenses: Optional[float] = None
    default_starting_savings: Optional[float] = None
    default_starting_debt: Optional[float] = None
    default_aspirations: dict = {}


class UpdateOnboardingDefaultsRequest(SQLModel):
    """Request model for updating account onboarding defaults"""
    age: int = Field(ge=15, le=35)
    city: str
    education_path: str
    risk_attitude: str
    monthly_income: float = Field(gt=0)
    monthly_expenses: float = Field(ge=0)
    starting_savings: float = Field(default=0.0, ge=0)
    starting_debt: float = Field(default=0.0, ge=0)
    aspirations: dict = {}
