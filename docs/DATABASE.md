# LifeSim Backend - Database Documentation

## Overview

The LifeSim backend uses **SQLite** with **SQLModel** (a combination of SQLAlchemy and Pydantic) for database operations. This provides type safety, async support, and seamless integration with FastAPI.

## Database Models

### 1. PlayerProfile
Stores the player's initial profile data from onboarding.

**Fields:**
- `id`: Primary key
- `session_id`: Unique identifier for the game session (UUID)
- `age`: Player's age (15-35)
- `city`: City of residence (affects cost of living)
- `education_path`: Vocational, University, High School, or Working
- `risk_attitude`: Risk Averse, Balanced, or Risk Seeking
- `starting_savings`: Initial savings amount
- `starting_debt`: Initial debt amount
- `aspirations`: JSON field for goals (own_car, travel, own_pet, etc.)
- `created_at`: Timestamp

**Relationships:**
- One-to-one with `GameState`
- One-to-many with `DecisionHistory`

### 2. GameState
Stores the current state of a player's game session. Updated after each decision.

**Financial Metrics:**
- `money`: Current cash/savings
- `monthly_income`: Monthly income
- `monthly_expenses`: Monthly cost of living
- `investments`: Value of investment portfolio
- `passive_income`: Monthly passive income from investments
- `debts`: Total debt amount
- `fi_score`: Financial Independence Score (0-100%)

**Life Metrics:**
- `energy`: Energy level (0-100)
- `motivation`: Motivation level (0-100)
- `social_life`: Social life quality (0-100)
- `financial_knowledge`: Financial literacy level (0-100)

**Other Fields:**
- `current_step`: Current event/decision number
- `game_status`: Active, Completed, or Abandoned
- `assets`: JSON field for owned items (car, pet, etc.)
- `risk_factors`: JSON field for curveball probability factors

### 3. DecisionHistory
Records each decision made by the player for replay and analysis.

**Fields:**
- `step_number`: Which decision this was
- `event_type`: Type of event (paycheck, unexpected_expense, curveball)
- `narrative`: The story presented to the player
- `options_presented`: List of decision options (JSON)
- `chosen_option`: The option the player selected
- `money_before/after`: Money before and after decision
- `fi_score_before/after`: FI score before and after
- `energy/motivation/social_before/after`: Life metrics before and after
- `consequence_narrative`: AI-generated explanation of consequences
- `learning_moment`: Optional educational insight
- `created_at`: Timestamp

### 4. LeaderboardEntry
Stores completed game results for the leaderboard.

**Fields:**
- `session_id`: Reference to the game session
- `player_nickname`: Optional display name
- `age`, `education_path`: Basic player info
- `final_fi_score`: Final Financial Independence Score
- `final_money`, `final_energy`, etc.: Final metric values
- `balance_score`: Average of energy, motivation, social life
- `steps_completed`: Number of decisions made
- `total_income_earned`, `total_spent`: Financial summary
- `best_decision`, `worst_decision`: Notable choices
- `completed_at`: Timestamp

## Key Calculations

### FI Score
```python
FI Score = (Passive Income / Monthly Expenses) × 100%
```
- 0%: Just starting, no passive income
- 25%: Good progress
- 50%: Halfway to financial independence
- 100%: Financially independent! 🎉

### Balance Score
```python
Balance Score = (Energy + Motivation + Social Life) / 3
```
Measures overall life quality, not just financial success.

### Net Worth
```python
Net Worth = Cash + Investments + Asset Value - Debts
```

## Database Setup

### Installation
```bash
pip install -r requirements.txt
```

### Initialization
The database is automatically initialized on FastAPI startup via the lifespan context manager in `main.py`.

### Manual Initialization (if needed)
```python
from database import create_db_and_tables
create_db_and_tables()
```

## API Endpoints

### POST /api/onboarding
Create a new player profile and initialize game state.

**Request:**
```json
{
  "age": 20,
  "city": "Helsinki",
  "education_path": "university",
  "risk_attitude": "balanced",
  "starting_savings": 1000,
  "starting_debt": 0,
  "aspirations": {
    "own_car": true,
    "travel": true,
    "own_pet": false
  }
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "current_step": 0,
  "money": 1000,
  "monthly_income": 2500,
  "monthly_expenses": 1200,
  "investments": 0,
  "passive_income": 0,
  "debts": 0,
  "fi_score": 0,
  "energy": 70,
  "motivation": 70,
  "social_life": 70,
  "financial_knowledge": 30,
  "assets": {},
  "game_status": "active"
}
```

### GET /api/game/{session_id}
Get current game state for a session.

### GET /api/leaderboard?limit=10
Get top players from the leaderboard.

## Utility Functions

Located in `utils.py`:

- `calculate_fi_score()`: Calculate Financial Independence Score
- `calculate_balance_score()`: Calculate life balance score
- `calculate_net_worth()`: Calculate total net worth
- `get_starting_income()`: Determine starting income based on profile
- `get_starting_expenses()`: Calculate starting expenses
- `initialize_game_state()`: Create initial game state from profile
- `update_metric()`: Update life metrics with bounds checking
- `calculate_investment_return()`: Calculate investment growth
- `calculate_debt_with_interest()`: Calculate debt with interest
- `assess_financial_health()`: Get health assessment categories

## Usage Example

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import PlayerProfile, GameState
from utils import calculate_fi_score

async def example(session: AsyncSession):
    # Create a player
    profile = PlayerProfile(
        session_id="test-123",
        age=22,
        city="Helsinki",
        education_path="university",
        risk_attitude="balanced",
        starting_savings=2000,
        starting_debt=0,
        aspirations={"own_car": True}
    )
    session.add(profile)
    await session.commit()
    
    # Query players
    result = await session.execute(select(PlayerProfile))
    profiles = result.scalars().all()
    
    # Update game state
    result = await session.execute(
        select(GameState).where(GameState.profile_id == profile.id)
    )
    game_state = result.scalar_one()
    game_state.money += 500
    game_state.fi_score = calculate_fi_score(
        game_state.passive_income,
        game_state.monthly_expenses
    )
    await session.commit()
```

## Database File

The SQLite database file is stored as `lifesim.db` in the backend directory. This can be configured via the `DATABASE_URL` environment variable in `.env`:

```bash
DATABASE_URL=sqlite:///./lifesim.db
```

## Next Steps

1. Implement the `/api/step` endpoint for processing decisions
2. Add AI integration for narrative generation
3. Implement curveball event system
4. Add decision simulation logic
5. Create `/api/finish` endpoint to save to leaderboard

## Development Tips

- Use `echo=True` in database.py during development to see SQL queries
- Set `echo=False` in production
- The database is recreated on each startup during development
- For production, implement proper migrations with Alembic
- All database operations should use async/await
- Use `Depends(get_session)` to inject database sessions in endpoints
