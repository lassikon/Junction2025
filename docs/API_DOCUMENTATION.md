# LifeSim API Endpoint Documentation

## Game Flow

1. **POST /api/onboarding** - Create player and get first event
2. **POST /api/step** - Make decision and get next event (repeat)
3. **GET /api/game/{session_id}** - Check current state anytime
4. **GET /api/leaderboard** - View top players

---

## Endpoints

### POST /api/onboarding

Create a new player profile and start the game.

**Request Body:**
```json
{
  "age": 22,
  "city": "Helsinki",
  "education_path": "university",
  "risk_attitude": "balanced",
  "starting_savings": 2000,
  "starting_debt": 0,
  "aspirations": {
    "own_car": true,
    "travel": true,
    "own_pet": false
  }
}
```

**Fields:**
- `age`: 15-35 (integer)
- `city`: "Helsinki", "Tampere", "Turku", etc.
- `education_path`: "vocational", "university", "high_school", "working"
- `risk_attitude`: "risk_averse", "balanced", "risk_seeking"
- `starting_savings`: 0+ (float)
- `starting_debt`: 0+ (float)
- `aspirations`: Object with boolean flags

**Response:**
```json
{
  "game_state": {
    "session_id": "uuid-here",
    "current_step": 0,
    "money": 2000.0,
    "monthly_income": 2700.0,
    "monthly_expenses": 1400.0,
    "investments": 0.0,
    "passive_income": 0.0,
    "debts": 0.0,
    "fi_score": 0.0,
    "energy": 70,
    "motivation": 70,
    "social_life": 70,
    "financial_knowledge": 30,
    "assets": {"car": {"type": "used_sedan", "value": 5000}},
    "game_status": "active"
  },
  "initial_narrative": "Congratulations! Your first paycheck just arrived...",
  "initial_options": [
    "Save 50% in emergency fund, spend the rest",
    "Invest 30% in index funds, save 20%, enjoy 50%",
    "Celebrate with friends and treat yourself",
    "Save 80% aggressively for future goals"
  ]
}
```

---

### POST /api/step

Process a player's decision and progress the game.

**Request Body:**
```json
{
  "session_id": "uuid-from-onboarding",
  "chosen_option": "Save 50% in emergency fund, spend the rest"
}
```

**Response:**
```json
{
  "consequence_narrative": "Great choice! You now have €3,350 in savings. Building an emergency fund gives you peace of mind and financial security...",
  "updated_state": {
    "session_id": "uuid-here",
    "current_step": 1,
    "money": 3350.0,
    "monthly_income": 2700.0,
    "monthly_expenses": 1400.0,
    "investments": 0.0,
    "passive_income": 0.0,
    "debts": 0.0,
    "fi_score": 0.0,
    "energy": 70,
    "motivation": 75,
    "social_life": 70,
    "financial_knowledge": 35,
    "assets": {"car": {"type": "used_sedan", "value": 5000}},
    "game_status": "active"
  },
  "next_narrative": "You've been tracking your spending and it's time to get more intentional with budgeting...",
  "next_options": [
    "Create a detailed budget using the 50/30/20 rule",
    "Use a budgeting app to automate tracking",
    "Keep rough mental track of spending"
  ],
  "learning_moment": "Financial experts recommend saving 3-6 months of expenses as an emergency fund before investing."
}
```

**Notes:**
- `learning_moment` appears ~30% of the time with educational tips
- Decisions update all metrics (money, life metrics, FI score)
- Each step increments `current_step`
- Events include both planned progression and random curveballs

---

### GET /api/game/{session_id}

Retrieve current game state for a session.

**Response:**
```json
{
  "session_id": "uuid-here",
  "current_step": 5,
  "money": 5200.0,
  "monthly_income": 2900.0,
  "monthly_expenses": 1450.0,
  "investments": 2000.0,
  "passive_income": 10.0,
  "debts": 0.0,
  "fi_score": 0.69,
  "energy": 65,
  "motivation": 80,
  "social_life": 60,
  "financial_knowledge": 55,
  "assets": {"car": {"type": "used_sedan", "value": 5000}},
  "game_status": "active"
}
```

---

### GET /api/leaderboard?limit=10

Get top players by FI Score.

**Query Parameters:**
- `limit`: Number of entries to return (default: 10)

**Response:**
```json
[
  {
    "rank": 1,
    "player_nickname": "FinancialNinja",
    "final_fi_score": 45.5,
    "balance_score": 72.3,
    "age": 24,
    "education_path": "university",
    "completed_at": "2025-11-14T19:30:00"
  },
  {
    "rank": 2,
    "player_nickname": "Anonymous",
    "final_fi_score": 38.2,
    "balance_score": 65.0,
    "age": 20,
    "education_path": "vocational",
    "completed_at": "2025-11-14T18:45:00"
  }
]
```

---

## Event Types

The game includes various event types that adapt to player state:

**Progression Events:**
- `first_paycheck`: Initial income decision
- `budget_decision`: Budgeting strategy
- `emergency_fund`: Building safety net
- `investment_opportunity`: Investing decisions
- `career_opportunity`: Career growth vs. work-life balance
- `lifestyle_choice`: Health and wellness spending
- `debt_management`: Handling debts strategically
- `social_event`: Social connections vs. saving
- `education_opportunity`: Financial education

**Curveball Events** (random, based on risk factors):
- Car repairs (if has_car)
- Insurance increases (if has_car)
- Vet bills (if has_pet)
- Rent increases (if has_rental)
- Tax refunds (positive)
- Bonuses (positive)
- Trip opportunities

---

## Game Mechanics

### Financial Independence (FI) Score
```
FI Score = (Passive Income / Monthly Expenses) × 100%
```
- 0%: Just starting
- 25%: Good progress
- 50%: Halfway there!
- 100%: Financially independent! 🎉

### Balance Score
```
Balance Score = (Energy + Motivation + Social Life) / 3
```
- Measures overall life quality
- Prevent burnout by maintaining balance
- High FI Score with low balance = "bad ending"

### Decision Effects
Each decision can affect:
- **Financial:** money, investments, debt, income, expenses, passive income
- **Life metrics:** energy (0-100), motivation (0-100), social_life (0-100), knowledge (0-100)
- **Assets:** car, pet, home ownership
- **Risk factors:** Affect curveball probability

---

## Testing with cURL

```bash
# 1. Create a player
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

# Save the session_id from the response

# 2. Make a decision
curl -X POST http://localhost:8000/api/step \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id-here",
    "chosen_option": "Save 50% in emergency fund, spend the rest"
  }'

# 3. Check game state
curl http://localhost:8000/api/game/your-session-id-here

# 4. View leaderboard
curl http://localhost:8000/api/leaderboard?limit=5
```

---

## Error Responses

**404 - Not Found:**
```json
{
  "detail": "Session not found"
}
```

**400 - Bad Request:**
```json
{
  "detail": "Invalid option chosen"
}
```

**500 - Server Error:**
```json
{
  "detail": "Error processing decision: ..."
}
```

---

## AI Integration

The API uses Gemini AI to generate:
- **Event narratives**: Context-aware stories adapted to player profile
- **Consequence narratives**: Personalized feedback on decisions
- **Learning moments**: Educational insights (appears ~30% of the time)

**Tone adaptation:**
- Risk-averse players: Reassuring and supportive
- Balanced players: Practical and straightforward
- Risk-seeking players: Exciting and opportunity-focused

**Fallback:** If AI is unavailable, uses pre-written fallback narratives.

---

## Next Steps

For complete game implementation, add:
1. **POST /api/finish** - Complete game and save to leaderboard
2. Game completion logic (max steps or FI score threshold)
3. Summary report generation
4. Best/worst decision analysis
5. Teacher mode for classroom use
