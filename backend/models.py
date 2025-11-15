"""
Database models for LifeSim: Financial Independence Quest

This module defines the SQLModel models for:
- Player profile and state
- Game sessions
- Decision history
- Leaderboard entries
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
