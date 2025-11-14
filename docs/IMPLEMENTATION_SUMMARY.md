# LifeSim Backend Setup - Complete! ✅

## What We've Implemented

### 1. Database Models (`models.py`)
Complete SQLModel models for:
- **PlayerProfile**: Stores onboarding data (age, city, education, risk attitude, aspirations)
- **GameState**: Tracks current game state (money, income, expenses, FI score, life metrics)
- **DecisionHistory**: Records every decision for replay and analysis
- **LeaderboardEntry**: Stores completed game results

### 2. Database Configuration (`database.py`)
- SQLite with async support (aiosqlite)
- Async session management for FastAPI
- Auto-initialization on app startup
- Clean shutdown on app close

### 3. Utility Functions (`utils.py`)
Pure functions for game mechanics:
- `calculate_fi_score()`: FI Score = (Passive Income / Monthly Expenses) × 100%
- `calculate_balance_score()`: Average of energy, motivation, social life
- `initialize_game_state()`: Set up initial state based on profile
- `get_starting_income()`: Income based on education and age
- `get_starting_expenses()`: Expenses based on city and lifestyle
- `assess_financial_health()`: Overall health categories

### 4. API Endpoints (`main.py`)
- **POST /api/onboarding**: Create new player and initialize game
- **GET /api/game/{session_id}**: Get current game state
- **GET /api/leaderboard**: Get top players
- Database lifecycle managed via FastAPI lifespan

### 5. Testing (`test_db.py`)
Complete test script that verifies:
- Database creation
- Profile creation
- Game state initialization
- State updates
- Decision history
- Queries

## Test Results ✅
```
🎉 All tests passed successfully!
✅ Database initialized
✅ Profile created
✅ Game state initialized with proper calculations
✅ Queries working
✅ Updates working
✅ Decision history working
```

## File Structure
```
backend/
├── main.py              # FastAPI app with endpoints
├── models.py            # SQLModel database models
├── database.py          # Database connection & session management
├── utils.py             # Game mechanics & calculations
├── test_db.py           # Test script
├── DATABASE.md          # Complete documentation
├── requirements.txt     # Dependencies
└── lifesim.db          # SQLite database (created on first run)
```

## Key Metrics Tracked

### Financial Metrics
- Money (cash/savings)
- Monthly income & expenses
- Investments
- Passive income
- Debts
- **FI Score**: 0-100% (financial independence percentage)

### Life Metrics (0-100 scale)
- Energy
- Motivation
- Social Life
- Financial Knowledge

## Starting Conditions (Example)

For a 22-year-old university student in Helsinki:
- Monthly Income: €2,700
- Monthly Expenses: €1,400
- Starting Savings: €2,000
- Energy/Motivation/Social: 70/100
- Financial Knowledge: 30/100

## Next Steps for Full Implementation

### Backend Tasks:
1. **Implement `/api/step` endpoint** - Process player decisions
   - Receive chosen option
   - Update game state
   - Call AI for consequence narrative
   - Generate next event and options
   
2. **Add AI Integration** - Connect to Gemini API
   - Generate event narratives
   - Create decision options
   - Produce consequence explanations
   - Add learning moments

3. **Implement Curveball System**
   - Random event generator
   - Risk factor probability calculations
   - Unexpected expenses/windfalls

4. **Add `/api/finish` endpoint**
   - Calculate final scores
   - Save to leaderboard
   - Generate summary report

### Frontend Integration:
The API is ready for frontend to:
1. Submit onboarding form → receive initial game state
2. Display metrics (money, FI%, energy, motivation, social, knowledge)
3. Show narrative and options
4. Submit decisions → receive updated state
5. Display leaderboard

## How to Run

### Start the server:
```bash
cd backend
uvicorn main:app --reload
```

### Test the API:
```bash
# Health check
curl http://localhost:8000/health

# Create a player
curl -X POST http://localhost:8000/api/onboarding \
  -H "Content-Type: application/json" \
  -d '{
    "age": 22,
    "city": "Helsinki",
    "education_path": "university",
    "risk_attitude": "balanced",
    "starting_savings": 2000,
    "starting_debt": 0,
    "aspirations": {"own_car": true, "travel": true}
  }'

# Get leaderboard
curl http://localhost:8000/api/leaderboard
```

### Run tests:
```bash
python test_db.py
```

## Dependencies Installed
- FastAPI >= 0.115.0
- Uvicorn >= 0.32.0
- Pydantic >= 2.10.0 (Python 3.13 compatible)
- SQLModel >= 0.0.22
- aiosqlite >= 0.20.0
- greenlet >= 3.0.0
- Plus existing: python-dotenv, httpx, openai, anthropic, google-genai

## Documentation
- Complete API documentation: `DATABASE.md`
- Interactive API docs: http://localhost:8000/docs (when server is running)
- ReDoc: http://localhost:8000/redoc

## Notes
- Database is SQLite for easy development and hackathon use
- All operations are async for better performance
- Proper error handling and validation via Pydantic
- Type-safe with SQLModel
- Ready for AI integration
- Scalable structure for future features
