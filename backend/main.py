from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
from google import genai
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from database import init_db, close_db, get_session
from models import (
    PlayerProfile, GameState, DecisionHistory, LeaderboardEntry,
    OnboardingRequest, GameStateResponse, GameStatus
)
from utils import initialize_game_state, generate_session_id, calculate_fi_score

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes database on startup and closes connections on shutdown.
    """
    # Startup
    print("🚀 Starting up LifeSim API...")
    await init_db()
    yield
    # Shutdown
    print("👋 Shutting down LifeSim API...")
    await close_db()


app = FastAPI(
    title="LifeSim: Financial Independence Quest API",
    lifespan=lifespan
)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY:", GEMINI_API_KEY)
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    message: str
    model: Optional[str] = "gemini-2.0-flash-exp"


class ChatResponse(BaseModel):
    response: str
    model: str


@app.get("/")
async def root():
    return {"message": "AI Hackathon API is running!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Basic chat endpoint - integrate with OpenAI, Anthropic, or other LLM providers
    """
    try:
        if not GEMINI_API_KEY or not client:
            raise HTTPException(
                status_code=500, detail="GEMINI_API_KEY not configured")

        # Map of valid Gemini models
        valid_models = ["gemini-2.0-flash-exp",
                        "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]

        # Use default model if provided model is not a Gemini model
        model_to_use = chat_message.model if chat_message.model in valid_models else "gemini-2.0-flash-exp"

        print("Requested model:", chat_message.model)
        print("Using model:", model_to_use)
        print("Message:", chat_message.message)

        # Generate response using the new genai.Client API
        response = client.models.generate_content(
            model=model_to_use,
            contents=chat_message.message
        )

        print("Response object:", response)
        print("Response text:", response.text)

        return ChatResponse(
            response=response.text,
            model=chat_message.model
        )
    except HTTPException:
        raise
    except Exception as e:
        print("Error details:", str(e))
        print("Error type:", type(e).__name__)
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating response: {str(e)}")


@app.get("/api/models")
async def list_models():
    """
    List available models
    """
    return {
        "models": [
            {"id": "gemini-2.0-flash-exp",
                "name": "Gemini 2.0 Flash (Experimental)"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
            {"id": "gemini-pro", "name": "Gemini Pro"},
        ]
    }


# =====================================================
# LifeSim Game Endpoints
# =====================================================

@app.post("/api/onboarding", response_model=GameStateResponse)
async def create_player(
    request: OnboardingRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new player profile and initialize game state.
    This is the first endpoint called when starting a new game.
    """
    try:
        # Generate unique session ID
        session_id = generate_session_id()

        # Create player profile
        profile = PlayerProfile(
            session_id=session_id,
            age=request.age,
            city=request.city,
            education_path=request.education_path,
            risk_attitude=request.risk_attitude,
            starting_savings=request.starting_savings,
            starting_debt=request.starting_debt,
            aspirations=request.aspirations
        )

        session.add(profile)
        await session.flush()  # Get the profile ID

        # Initialize game state
        initial_state = initialize_game_state(profile)
        game_state = GameState(
            profile_id=profile.id,
            **initial_state
        )

        # Calculate initial FI score
        game_state.fi_score = calculate_fi_score(
            game_state.passive_income,
            game_state.monthly_expenses
        )

        session.add(game_state)
        await session.commit()
        await session.refresh(game_state)

        # Return initial game state
        return GameStateResponse(
            session_id=session_id,
            current_step=game_state.current_step,
            money=game_state.money,
            monthly_income=game_state.monthly_income,
            monthly_expenses=game_state.monthly_expenses,
            investments=game_state.investments,
            passive_income=game_state.passive_income,
            debts=game_state.debts,
            fi_score=game_state.fi_score,
            energy=game_state.energy,
            motivation=game_state.motivation,
            social_life=game_state.social_life,
            financial_knowledge=game_state.financial_knowledge,
            assets=game_state.assets,
            game_status=game_state.game_status
        )

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating player: {str(e)}")


@app.get("/api/game/{session_id}", response_model=GameStateResponse)
async def get_game_state(
    session_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get current game state for a session.
    """
    try:
        # Find the profile
        result = await session.execute(
            select(PlayerProfile).where(PlayerProfile.session_id == session_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get game state
        result = await session.execute(
            select(GameState).where(GameState.profile_id == profile.id)
        )
        game_state = result.scalar_one_or_none()

        if not game_state:
            raise HTTPException(status_code=404, detail="Game state not found")

        return GameStateResponse(
            session_id=session_id,
            current_step=game_state.current_step,
            money=game_state.money,
            monthly_income=game_state.monthly_income,
            monthly_expenses=game_state.monthly_expenses,
            investments=game_state.investments,
            passive_income=game_state.passive_income,
            debts=game_state.debts,
            fi_score=game_state.fi_score,
            energy=game_state.energy,
            motivation=game_state.motivation,
            social_life=game_state.social_life,
            financial_knowledge=game_state.financial_knowledge,
            assets=game_state.assets,
            game_status=game_state.game_status
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving game state: {str(e)}")


@app.get("/api/leaderboard", response_model=List[dict])
async def get_leaderboard(
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    """
    Get top players from the leaderboard.
    """
    try:
        result = await session.execute(
            select(LeaderboardEntry)
            .order_by(LeaderboardEntry.final_fi_score.desc())
            .limit(limit)
        )
        entries = result.scalars().all()

        return [
            {
                "rank": idx + 1,
                "player_nickname": entry.player_nickname or "Anonymous",
                "final_fi_score": entry.final_fi_score,
                "balance_score": entry.balance_score,
                "age": entry.age,
                "education_path": entry.education_path,
                "completed_at": entry.completed_at.isoformat()
            }
            for idx, entry in enumerate(entries)
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving leaderboard: {str(e)}")
