# AI Hackathon - Junction 2025

Quick Docker setup with React frontend and Python FastAPI backend for AI/LLM development.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- API keys for LLM services (OpenAI, Anthropic, etc.)

### Setup

1. **Configure Backend Environment**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your API keys
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
│   ├── Dockerfile
│   ├── main.py              # FastAPI application with game endpoints
│   ├── models.py            # SQLModel database models
│   ├── database.py          # Database configuration & sessions
│   ├── utils.py             # Game mechanics & calculations
│   ├── test_db.py           # Database test script
│   ├── requirements.txt     # Python dependencies
│   ├── DATABASE.md          # Database documentation
│   ├── IMPLEMENTATION_SUMMARY.md  # Setup summary
│   └── .env                 # Environment variables (create this)
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.js           # Main React component
│       ├── App.css
│       └── index.js
├── docs/
│   └── LifeSim_Financial_Independence_Quest_Plan.md  # Project plan
└── docker-compose.yml       # Docker orchestration
```

## 🛠️ Development

### Backend (FastAPI)
- Auto-reloads on code changes
- API documentation at `/docs`
- Includes CORS for frontend communication
- Pre-configured with OpenAI & Anthropic packages

### Frontend (React)
- Hot-reload enabled
- Axios for API calls
- Clean chat interface
- API status indicator

### Available Endpoints

**GET** `/` - Root endpoint
**GET** `/health` - Health check
**POST** `/api/chat` - Chat with AI
**GET** `/api/models` - List available models

#### LifeSim Game Endpoints
**POST** `/api/onboarding` - Create new player and initialize game
**GET** `/api/game/{session_id}` - Get current game state
**GET** `/api/leaderboard` - Get top players

See `backend/DATABASE.md` for complete API documentation.

## 🧪 Testing the Setup

1. Open http://localhost:4000
2. You should see "API: connected" if backend is running
3. Type a message - it will echo back (update `/api/chat` for real LLM integration)

## 🔧 Customization

### Add LLM Integration
Edit `backend/main.py` in the `/api/chat` endpoint:
```python
import openai
# Add your LLM logic here
```

### Environment Variables
Add to `backend/.env`:
```
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

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

## 🎯 Hackathon Tips

- Backend has OpenAI & Anthropic packages pre-installed
- Use `/api/chat` endpoint for LLM integration
- Frontend is styled and ready for demos
- Hot-reload works in both frontend and backend
- Check logs: `docker-compose logs -f`

Good luck at Junction 2025! 🚀
