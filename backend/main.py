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
    OnboardingRequest, GameStateResponse, OnboardingResponse, GameStatus,
    DecisionRequest, DecisionResponse
)
from utils import initialize_game_state, generate_session_id, calculate_fi_score
from game_engine import (
    get_event_type, create_decision_options, apply_decision_effects,
    setup_option_effect, generate_curveball_event
)
from ai_narrative import (
    generate_event_narrative, generate_consequence_narrative,
    generate_learning_moment, generate_option_texts
)

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
    description="""
    ## LifeSim Financial Independence Quest
    
    An interactive game that teaches financial literacy through life decisions.
    
    ### Features:
    * **Onboarding**: Create personalized player profiles
    * **Game Progression**: Navigate through life stages with financial decisions
    * **Decision Making**: Make choices that impact your financial health
    * **Leaderboard**: Compete with other players on Financial Independence Score
    * **AI-Generated Narratives**: Dynamic storytelling powered by Gemini AI
    
    ### Game Flow:
    1. Complete onboarding to set up your profile
    2. Receive life events and make decisions
    3. See consequences of your choices
    4. Progress through life stages
    5. Aim for financial independence!
    """,
    version="1.0.0",
    contact={
        "name": "Junction2025 Team",
        "url": "https://github.com/lassikon/Junction2025",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc alternative documentation
    openapi_url="/openapi.json",  # OpenAPI schema
    lifespan=lifespan
)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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


# Database tables are managed by Alembic migrations
# Run: alembic upgrade head
# See: MIGRATIONS_README.md for more info
@app.on_event("startup")
def on_startup():
    # create_db_and_tables()  # Disabled - use Alembic migrations instead
    pass


class ChatMessage(BaseModel):
    message: str
    model: Optional[str] = "gemini-2.0-flash-exp"


class ChatResponse(BaseModel):
    response: str
    model: str


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - API welcome message
    """
    return {"message": "AI Hackathon API is running!"}


@app.get("/health", tags=["System"])
async def health():
    """
    Health check endpoint - verify API is operational
    """
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse, tags=["AI"])
async def chat(chat_message: ChatMessage, session: AsyncSession = Depends(get_session)):
    """
    Chat with AI using Gemini models
    
    Send a message to the AI and receive a response powered by Google's Gemini.
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


@app.get("/api/models", tags=["AI"])
async def list_models():
    """
    List available AI models
    
    Get a list of all available Gemini models that can be used for chat.
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

@app.post("/api/onboarding", response_model=OnboardingResponse, tags=["Game"])
async def create_player(
    request: OnboardingRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new player profile and start the game
    
    This is the first endpoint called when starting a new game.
    
    **Process:**
    1. Creates a player profile with provided information
    2. Initializes game state with starting values
    3. Generates the first life event and decision options
    4. Returns session_id for subsequent API calls
    
    **Returns:** Initial game state with narrative and decision options
    """
    try:
        # Generate unique session ID
        session_id = generate_session_id()

        # Create player profile
        profile = PlayerProfile(
            session_id=session_id,
            player_name=request.player_name,
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

        # Generate initial narrative and options
        initial_event_type = get_event_type(game_state, profile)

        initial_narrative = generate_event_narrative(
            event_type=initial_event_type,
            state=game_state,
            profile=profile,
            curveball=None,
            client=client
        )

        initial_options_data = create_decision_options(
            initial_event_type, game_state, None)

        # Generate option texts with AI
        initial_options = generate_option_texts(
            initial_options_data,
            initial_event_type,
            game_state,
            profile,
            client
        )

        # Store the generated texts back in the options data with indices
        for i, opt in enumerate(initial_options_data):
            opt["text"] = initial_options[i]
            # Add index for reliable matching later        # Build game state response
            opt["index"] = i
        game_state_response = GameStateResponse(
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

        return OnboardingResponse(
            game_state=game_state_response,
            initial_narrative=initial_narrative,
            initial_options=initial_options
        )

    except Exception as e:
        await session.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error creating player: {str(e)}")


@app.get("/api/game/{session_id}", response_model=GameStateResponse, tags=["Game"])
async def get_game_state(
    session_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get current game state for a session
    
    Retrieve the current financial status, life stage, and game progress
    for an active game session.
    
    **Parameters:**
    - **session_id**: Unique session identifier from onboarding
    
    **Returns:** Current game state with all financial metrics
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


@app.get("/api/leaderboard", response_model=List[dict], tags=["Leaderboard"])
async def get_leaderboard(
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    """
    Get top players from the leaderboard
    
    Retrieve the highest-scoring players based on Financial Independence Score.
    
    **Parameters:**
    - **limit**: Maximum number of players to return (default: 10)
    
    **Returns:** List of top players with their scores and achievements
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


@app.post("/api/step", response_model=DecisionResponse, tags=["Game"])
async def process_decision(
    request: DecisionRequest,
    db_session: AsyncSession = Depends(get_session)
):
    """
    Process a player's decision and advance the game
    
    Main gameplay endpoint that processes decisions and progresses the story.

    **Process:**
    1. Retrieves current game state
    2. Applies the chosen decision's effects to finances and stats
    3. Records the decision in history
    4. Generates consequence narrative with AI
    5. Creates the next event and decision options
    6. Updates life stage if applicable
    
    **Parameters:**
    - **session_id**: Current game session identifier
    - **decision_index**: Index of the chosen decision option
    
    **Returns:** Updated game state, consequence narrative, and next decision options
    """
    try:
        # Get player profile and game state
        result = await db_session.execute(
            select(PlayerProfile).where(
                PlayerProfile.session_id == request.session_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(status_code=404, detail="Session not found")

        result = await db_session.execute(
            select(GameState).where(GameState.profile_id == profile.id)
        )
        game_state = result.scalar_one_or_none()

        if not game_state:
            raise HTTPException(status_code=404, detail="Game state not found")

        if game_state.game_status != GameStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Game is not active")

        # Get the current event type for this step
        # (We need to recreate it to find the matching option)
        current_event_type = get_event_type(game_state, profile)

        # Generate curveball if needed
        curveball = None
        if current_event_type == "curveball":
            curveball = generate_curveball_event(game_state)

        # Get available options for current state
        available_options = create_decision_options(
            current_event_type, game_state, curveball)

        # Always generate option texts for recording in history
        option_texts = generate_option_texts(
            available_options,
            current_event_type,
            game_state,
            profile,
            client
        )

        # Store texts in options for history recording
        for i, opt in enumerate(available_options):
            opt["text"] = option_texts[i]

        # Find the chosen option
        chosen_option_data = None
        chosen_index = -1

        # If frontend sent an index, use it directly (most reliable)
        if request.option_index is not None and 0 <= request.option_index < len(available_options):
            chosen_option_data = available_options[request.option_index]
            chosen_index = request.option_index
        else:
            # Fallback: try to match by text
            # Try exact match with generated text
            for i, text in enumerate(option_texts):
                if text == request.chosen_option:
                    chosen_option_data = available_options[i]
                    chosen_index = i
                    break

            # If exact match fails, try fallback_text match
            if not chosen_option_data:
                for i, option in enumerate(available_options):
                    if option.get("fallback_text", "") == request.chosen_option:
                        chosen_option_data = option
                        chosen_index = i
                        break

        if not chosen_option_data:
            raise HTTPException(
                status_code=400, detail=f"Invalid option chosen: {request.chosen_option}")

        # Store state before changes
        money_before = game_state.money
        investments_before = game_state.investments
        fi_before = game_state.fi_score
        energy_before = game_state.energy
        motivation_before = game_state.motivation
        social_before = game_state.social_life
        step_number = game_state.current_step

        # Apply decision effects
        effect = setup_option_effect(chosen_option_data)

        # Debug: Log effect details
        print(f"💰 APPLYING EFFECTS:")
        print(f"  Investment change: {effect.investment_change}")
        print(f"  Money change: {effect.money_change}")
        print(
            f"  Before - Investments: {investments_before}, Money: {money_before}")

        apply_decision_effects(game_state, effect)

        print(
            f"  After - Investments: {game_state.investments}, Money: {game_state.money}")

        # Generate consequence narrative
        consequence = generate_consequence_narrative(
            chosen_option=request.chosen_option,
            option_effect=chosen_option_data,
            state=game_state,
            profile=profile,
            client=client
        )

        # Generate learning moment (sometimes)
        learning = generate_learning_moment(
            chosen_option=request.chosen_option,
            state=game_state,
            profile=profile,
            client=client
        )

        # Record decision in history
        decision_record = DecisionHistory(
            profile_id=profile.id,
            step_number=step_number,
            event_type=current_event_type,
            narrative="",  # Will be filled from previous step's next_narrative
            options_presented=[opt["text"] for opt in available_options],
            chosen_option=request.chosen_option,
            money_before=money_before,
            fi_score_before=fi_before,
            energy_before=energy_before,
            motivation_before=motivation_before,
            social_before=social_before,
            money_after=game_state.money,
            fi_score_after=game_state.fi_score,
            energy_after=game_state.energy,
            motivation_after=game_state.motivation,
            social_after=game_state.social_life,
            consequence_narrative=consequence,
            learning_moment=learning
        )

        db_session.add(decision_record)

        # Update game state in database
        await db_session.commit()
        await db_session.refresh(game_state)

        # Generate next event
        next_event_type = get_event_type(game_state, profile)
        next_curveball = None
        if next_event_type == "curveball":
            next_curveball = generate_curveball_event(game_state)

        # Generate next narrative
        next_narrative = generate_event_narrative(
            event_type=next_event_type,
            state=game_state,
            profile=profile,
            curveball=next_curveball,
            client=client
        )

        # Generate next options
        next_options_data = create_decision_options(
            next_event_type, game_state, next_curveball)

        # Generate option texts with AI
        next_options = generate_option_texts(
            next_options_data,
            next_event_type,
            game_state,
            profile,
            client
        )

        # Store the generated texts back in the options data with indices
        for i, opt in enumerate(next_options_data):
            opt["text"] = next_options[i]
            opt["index"] = i  # Add index for reliable matching later

        # Build updated state response
        updated_state = GameStateResponse(
            session_id=request.session_id,
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

        print(
            f"📤 RESPONSE - Investments being sent: {updated_state.investments}")

        return DecisionResponse(
            consequence_narrative=consequence,
            updated_state=updated_state,
            next_narrative=next_narrative,
            next_options=next_options,
            learning_moment=learning
        )

    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing decision: {str(e)}")
