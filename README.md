# LifeSim - Financial Independence Quest

An interactive financial education game powered by AI. Make life decisions, manage your finances, and work towards financial independence in a realistic simulation.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Setup

1. **Configure Backend Environment**
   ```bash
   cd backend
   # Create .env file with your Gemini API key
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

2. **Start Everything**
   ```bash
   docker-compose up --build
   ```

3. **Access the Application**
   - Frontend: http://localhost:4000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Stop Services
```bash
docker-compose down
```

## 📁 Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application with game endpoints
│   ├── models.py            # SQLModel database models
│   ├── database.py          # Database configuration & sessions
│   ├── game_engine.py       # Core game mechanics & decision effects
│   ├── ai_narrative.py      # Gemini AI narrative generation
│   ├── utils.py             # Helper functions & calculations
│   ├── chat_utils.py        # Chat history & summaries
│   ├── requirements.txt     # Python dependencies
│   ├── prompts/             # AI prompt templates
│   │   ├── narrative_prompt.json
│   │   ├── consequence_prompt.json
│   │   ├── learning_moment_prompt.json
│   │   └── fallback_narratives.json
│   └── .env                 # Environment variables (create this)
├── frontend/
│   ├── src/
│   │   ├── routes/          # Page components
│   │   │   ├── OnboardingPage.js
│   │   │   └── GamePage.js
│   │   ├── components/      # UI components
│   │   │   ├── GameDashboard.js
│   │   │   ├── SceneView.js
│   │   │   ├── ChoiceList.js
│   │   │   ├── MetricsBar.js
│   │   │   ├── ConsequenceModal.js
│   │   │   └── TopBar.js
│   │   ├── store/           # Zustand state management
│   │   │   └── gameStore.js
│   │   ├── api/             # TanStack Query API hooks
│   │   │   └── lifesim.js
│   │   └── hooks/           # Custom React hooks
│   └── package.json
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE.md
│   ├── EXPENSE_CATEGORIES_FRONTEND_GUIDE.md
│   └── TANSTACK_ZUSTAND_README.md
└── docker-compose.yml       # Docker orchestration
```

## 🎮 Game Features

- **AI-Generated Narratives**: Dynamic storytelling powered by Google Gemini 2.0 Flash
- **Financial Simulation**: Realistic income, expenses, investments, and debt management
- **Expense Breakdown**: Detailed expense categories (housing, food, transport, utilities, subscriptions, insurance, other)
- **Life Metrics**: Energy, motivation, social connections, and financial knowledge
- **Decision Making**: Choices with realistic consequences and trade-offs
- **Curveballs**: Random life events that test your financial resilience
- **Learning Moments**: Educational insights about personal finance
- **Progress Tracking**: Transaction history and FI score tracking

## 🛠️ Development

### Backend (FastAPI)
- Auto-reloads on code changes
- API documentation at `/docs`
- SQLite database with SQLModel ORM
- Google Gemini AI integration for narrative generation
- Background task processing for faster response times

### Frontend (React)
- Hot-reload enabled
- TanStack Query for server state management
- Zustand for client state management
- Responsive design with custom CSS

### Key API Endpoints

#### Authentication
- **POST** `/api/auth/register` - Create new account
- **POST** `/api/auth/login` - Login to existing account
- **POST** `/api/auth/logout` - Logout

#### Game
- **POST** `/api/onboarding` - Start new game (requires authentication)
- **GET** `/api/game/{session_id}` - Get current game state
- **POST** `/api/step` - Make a decision and advance the game
- **GET** `/api/next-question/{session_id}` - Fetch pre-generated next question
- **GET** `/api/transactions/{session_id}` - Get transaction history
- **GET** `/api/leaderboard` - View top players

#### Chat & AI
- **POST** `/api/chat` - Chat with AI about financial topics
- **GET** `/api/models` - List available AI models

See `docs/API_DOCUMENTATION.md` for complete API documentation.

## 🧪 Testing the Setup

1. Open http://localhost:4000
2. Create an account or login
3. Complete the onboarding (name, city, education, risk attitude)
4. Start playing! Make decisions and see your financial journey unfold

## 🔧 Configuration

### Environment Variables

**Required:**
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### AI Model Configuration

The game uses Google Gemini 2.0 Flash (Experimental) by default. Available models:
- `gemini-2.0-flash-exp` (recommended, fastest)
- `gemini-1.5-pro` (more capable, slower)
- `gemini-1.5-flash` (balanced)

To change the model, update the `model` parameter in `backend/ai_narrative.py`.

## 📦 Installing Additional Packages

### Backend
Add to `backend/requirements.txt`, then:
```bash
docker-compose up --build backend
```

### Frontend
Add to `frontend/package.json`, then:
```bash
docker-compose up --build frontend
```

## 🐛 Troubleshooting

**Missing Gemini API key:**
```bash
# Make sure .env file exists in backend/
cat backend/.env
# Should show: GEMINI_API_KEY=your_key_here
```

**Port already in use:**
```bash
# Change ports in docker-compose.yml
ports:
  - "4001:4000"  # Frontend
  - "8001:8000"  # Backend
```

**Frontend can't reach backend:**
- Check `REACT_APP_API_URL` in docker-compose.yml
- Verify CORS settings in `backend/main.py`

**Changes not reflecting:**
```bash
docker-compose down
docker-compose up --build
```

**AI not generating narratives:**
- Verify your Gemini API key is valid
- Check backend logs: `docker-compose logs backend`
- Ensure you have API quota remaining

## 📚 Documentation

- **API Reference**: `docs/API_DOCUMENTATION.md`
- **Database Schema**: `docs/DATABASE.md`
- **Expense Categories Guide**: `docs/EXPENSE_CATEGORIES_FRONTEND_GUIDE.md`
- **State Management**: `docs/TANSTACK_ZUSTAND_README.md`

## 🎯 Game Architecture

### Backend Flow
1. Player makes a decision → `POST /api/step`
2. AI generates consequence narrative (immediate response)
3. Effects applied to game state (money, metrics, expenses)
4. Next question generated in background and cached
5. Frontend fetches cached question → `GET /api/next-question/{session_id}`

### AI Prompt System
- **narrative_prompt.json**: Initial scenario generation
- **consequence_prompt.json**: Decision outcomes and effects
- **learning_moment_prompt.json**: Educational financial insights
- **fallback_narratives.json**: Backup narratives when AI unavailable

### Expense Breakdown System
Each player's monthly expenses are divided into 7 categories:
- Housing (40-45%): Rent/mortgage
- Food (25%): Groceries, dining
- Transport (8-12%): Public transport, car costs
- Utilities (12%): Bills, internet, phone
- Subscriptions (5%): Entertainment services
- Insurance (5-8%): Health, car, home
- Other (5-7%): Personal care, pets, misc

Players can reduce expenses through decisions (e.g., cancel subscriptions, reduce food budget), but face trade-offs in energy, motivation, or social connections.

---

Built for Junction 2025 🚀
