from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import time
from contextlib import contextmanager
from dotenv import load_dotenv
from google import genai
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from database import init_db, close_db, get_session
from models import (
    PlayerProfile, GameState, DecisionHistory, LeaderboardEntry, TransactionLog,
    OnboardingRequest, GameStateResponse, OnboardingResponse, GameStatus,
    DecisionRequest, DecisionResponse, ChatRequest, ChatResponse,
    ChatHistoryResponse, ChatMessageResponse, ChatRole, ChatSession, ChatMessage,
    LifeMetricsChanges, TransactionSummary, MonthlyCashFlowSummary
)
from utils import initialize_game_state, generate_session_id, calculate_fi_score
from game_engine import (
    get_event_type, create_decision_options, apply_decision_effects,
    setup_option_effect, generate_curveball_event, setup_dynamic_option_effect
)
from ai_narrative import (
    generate_event_narrative, generate_consequence_narrative,
    generate_learning_moment, generate_dynamic_options, get_ai_client
)
from rag_service import RAGService, get_rag_service
import rag_service as rag_module
from chat_utils import (
    get_or_create_chat_session, save_chat_message, should_create_summary,
    create_chat_summary, store_chat_summary, get_recent_chat_messages,
    get_latest_chat_summary
)
from chat_ai import generate_chat_response
from auth_utils import (
    hash_password, verify_password, create_session_token,
    validate_token, get_current_account, get_optional_account
)
from models import (
    Account, SessionToken, RegisterRequest, LoginRequest,
    AuthResponse, AccountProfileResponse, UpdateOnboardingDefaultsRequest
)

load_dotenv()


# =====================================================
# Performance Monitoring - Easy to remove
# =====================================================
@contextmanager
def timer(operation_name: str):
    """Context manager to time operations. Remove this block to disable timing."""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        print(f"⏱️  {operation_name}: {duration:.3f}s")
# =====================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes database on startup and closes connections on shutdown.
    """
    # Startup
    print("🚀 Starting up LifeSim API...")
    await init_db()

    # Initialize RAG service
    try:
        rag_module.rag_service = RAGService(
            chroma_host="chromadb", chroma_port=8000)
        print("✅ RAG Service initialized")
    except Exception as e:
        print(f"⚠️ RAG Service failed to initialize: {e}")
        print("   Game will continue without RAG-enhanced learning moments")
        rag_module.rag_service = None

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
    allow_origins=["http://localhost:4000"],
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


# =====================================================
# Authentication Endpoints
# =====================================================

@app.post("/api/auth/register", response_model=AuthResponse, tags=["Authentication"])
async def register(
    request: RegisterRequest,
    db_session: AsyncSession = Depends(get_session)
):
    """
    Register a new user account

    Creates a new account with hashed password and returns an auth token.

    **Process:**
    1. Validates username is unique
    2. Hashes password with bcrypt
    3. Creates account record
    4. Generates session token
    5. Returns token and account info

    **Parameters:**
    - **username**: Unique username (3-50 chars)
    - **password**: Password (min 6 chars)
    - **display_name**: Display name (1-100 chars)

    **Returns:** Auth token and account information
    """
    try:
        # Check if username already exists
        result = await db_session.execute(
            select(Account).where(Account.username == request.username.lower())
        )
        existing_account = result.scalar_one_or_none()

        if existing_account:
            raise HTTPException(
                status_code=400, detail="Username already taken")

        # Hash password
        password_hash = hash_password(request.password)

        # Create account
        account = Account(
            username=request.username.lower(),
            password_hash=password_hash,
            display_name=request.display_name,
            has_completed_onboarding=False
        )

        db_session.add(account)
        await db_session.flush()

        # Create session token
        token = await create_session_token(account.id, db_session)

        await db_session.commit()

        print(
            f"✅ Registered new account: {account.username} (ID: {account.id})")

        return AuthResponse(
            token=token,
            account_id=account.id,
            username=account.username,
            display_name=account.display_name,
            has_completed_onboarding=account.has_completed_onboarding
        )

    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error creating account: {str(e)}")


@app.post("/api/auth/login", response_model=AuthResponse, tags=["Authentication"])
async def login(
    request: LoginRequest,
    db_session: AsyncSession = Depends(get_session)
):
    """
    Login to existing account

    Validates credentials and returns an auth token.

    **Parameters:**
    - **username**: Account username
    - **password**: Account password

    **Returns:** Auth token and account information
    """
    try:
        # Find account
        result = await db_session.execute(
            select(Account).where(Account.username == request.username.lower())
        )
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=401, detail="Invalid username or password")

        # Verify password
        if not verify_password(request.password, account.password_hash):
            raise HTTPException(
                status_code=401, detail="Invalid username or password")

        # Update last login
        account.last_login = datetime.utcnow()

        # Create session token
        token = await create_session_token(account.id, db_session)

        await db_session.commit()

        print(f"✅ User logged in: {account.username} (ID: {account.id})")

        return AuthResponse(
            token=token,
            account_id=account.id,
            username=account.username,
            display_name=account.display_name,
            has_completed_onboarding=account.has_completed_onboarding
        )

    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error during login: {str(e)}")


@app.post("/api/auth/logout", tags=["Authentication"])
async def logout(
    authorization: str = Header(...),
    db_session: AsyncSession = Depends(get_session)
):
    """
    Logout and invalidate current session token

    **Headers:**
    - **Authorization**: Bearer {token}

    **Returns:** Success message
    """
    try:
        # Parse token
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=401, detail="Invalid authorization header")

        token = parts[1]

        # Find and deactivate token
        result = await db_session.execute(
            select(SessionToken).where(SessionToken.token == token)
        )
        session_token = result.scalar_one_or_none()

        if session_token:
            session_token.is_active = False
            await db_session.commit()

        return {"message": "Logged out successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error during logout: {str(e)}")


@app.get("/api/account/profile", response_model=AccountProfileResponse, tags=["Account"])
async def get_account_profile(
    authorization: str = Header(...),
    db_session: AsyncSession = Depends(get_session)
):
    """
    Get current account profile and onboarding defaults

    Requires authentication.

    **Headers:**
    - **Authorization**: Bearer {token}

    **Returns:** Account profile with onboarding defaults
    """
    # Parse and validate token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401, detail="Invalid authorization header")

    token = parts[1]
    account = await validate_token(token, db_session)
    if not account:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return AccountProfileResponse(
        account_id=account.id,
        username=account.username,
        display_name=account.display_name,
        created_at=account.created_at,
        has_completed_onboarding=account.has_completed_onboarding,
        default_age=account.default_age,
        default_city=account.default_city,
        default_education_path=account.default_education_path,
        default_risk_attitude=account.default_risk_attitude,
        default_monthly_income=account.default_monthly_income,
        default_monthly_expenses=account.default_monthly_expenses,
        default_starting_savings=account.default_starting_savings,
        default_starting_debt=account.default_starting_debt,
        default_aspirations=account.default_aspirations
    )


@app.put("/api/account/onboarding", tags=["Account"])
async def update_onboarding_defaults(
    request: UpdateOnboardingDefaultsRequest,
    authorization: str = Header(...),
    db_session: AsyncSession = Depends(get_session)
):
    """
    Update account onboarding defaults

    Saves onboarding data to account so user doesn't have to fill it out again.

    **Headers:**
    - **Authorization**: Bearer {token}

    **Parameters:** Onboarding data (see UpdateOnboardingDefaultsRequest)

    **Returns:** Success message
    """
    try:
        # Parse and validate token
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=401, detail="Invalid authorization header")

        token = parts[1]
        account = await validate_token(token, db_session)
        if not account:
            raise HTTPException(
                status_code=401, detail="Invalid or expired token")
        account.default_age = request.age
        account.default_city = request.city
        account.default_education_path = request.education_path
        account.default_risk_attitude = request.risk_attitude
        account.default_monthly_income = request.monthly_income
        account.default_monthly_expenses = request.monthly_expenses
        account.default_starting_savings = request.starting_savings
        account.default_starting_debt = request.starting_debt
        account.default_aspirations = request.aspirations
        account.has_completed_onboarding = True

        await db_session.commit()

        print(f"✅ Updated onboarding defaults for account: {account.username}")

        return {"message": "Onboarding defaults updated successfully"}

    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating defaults: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, db_session: AsyncSession = Depends(get_session)):
    """
    Send a chat message and receive game-aware AI response

    This endpoint provides an AI assistant that is aware of:
    - Your current game state (age, finances, FI score)
    - Your player profile (education, risk attitude, aspirations)
    - Recent chat history (with automatic summarization)
    - Recent game decisions

    **Process:**
    1. Retrieves or creates chat session for your game
    2. Saves your message to chat history
    3. Generates context-aware AI response
    4. Automatically creates summary every 10 messages
    5. Returns AI response

    **Parameters:**
    - **session_id**: Your game session ID
    - **message**: Your question or message
    - **model**: AI model to use (default: gemini-2.0-flash-exp)

    **Returns:** AI response with session and message tracking info
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

        # Get or create chat session
        chat_session = await get_or_create_chat_session(
            session_id=request.session_id,
            profile_id=profile.id,
            db_session=db_session
        )

        # Save user message
        user_message = await save_chat_message(
            chat_session=chat_session,
            role=ChatRole.USER,
            content=request.message,
            db_session=db_session,
            message_metadata={"model": request.model}
        )

        # Generate AI response
        ai_response_text = await generate_chat_response(
            user_message=request.message,
            chat_session=chat_session,
            game_state=game_state,
            profile=profile,
            db_session=db_session,
            client=client
        )

        # Save AI response
        ai_message = await save_chat_message(
            chat_session=chat_session,
            role=ChatRole.ASSISTANT,
            content=ai_response_text,
            db_session=db_session,
            message_metadata={"model": request.model}
        )

        # Check if we should create a summary
        if await should_create_summary(chat_session):
            print(
                f"📊 Creating summary for chat session (message count: {chat_session.message_count})")
            try:
                # Get messages for summary (last 10)
                summary_start = max(1, chat_session.message_count - 9)
                summary_end = chat_session.message_count

                messages_for_summary = await get_recent_chat_messages(
                    chat_session_id=chat_session.id,
                    db_session=db_session,
                    limit=10
                )

                summary_text = await create_chat_summary(
                    messages=messages_for_summary,
                    game_state=game_state,
                    profile=profile,
                    client=client
                )

                await store_chat_summary(
                    chat_session=chat_session,
                    summary_text=summary_text,
                    message_range_start=summary_start,
                    message_range_end=summary_end,
                    db_session=db_session
                )

                print(f"✅ Summary created: {summary_text[:100]}...")

            except Exception as e:
                print(f"⚠️ Failed to create summary: {e}")

        # Commit all changes
        await db_session.commit()
        await db_session.refresh(ai_message)

        return ChatResponse(
            response=ai_response_text,
            session_id=request.session_id,
            chat_session_id=chat_session.chat_session_id,
            message_id=ai_message.id,
            model=request.model
        )

    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing chat: {str(e)}")


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


@app.get("/api/chat/history/{session_id}", response_model=ChatHistoryResponse, tags=["Chat"])
async def get_chat_history(
    session_id: str,
    page: int = 1,
    page_size: int = 20,
    db_session: AsyncSession = Depends(get_session)
):
    """
    Get chat history for a game session with pagination

    Retrieves chat messages with automatic pagination and summarization.

    **Features:**
    - Paginated message retrieval (default 20 messages per page)
    - Automatic summary when history exceeds 10 messages
    - Messages ordered chronologically (oldest to newest)

    **Parameters:**
    - **session_id**: Game session ID
    - **page**: Page number (default: 1)
    - **page_size**: Messages per page (default: 20, max: 100)

    **Returns:** Chat messages, summary (if available), and pagination info
    """
    try:
        # Validate pagination params
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=400, detail="Page size must be between 1 and 100")

        # Get player profile
        result = await db_session.execute(
            select(PlayerProfile).where(PlayerProfile.session_id == session_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get chat session
        result = await db_session.execute(
            select(ChatSession).where(ChatSession.profile_id == profile.id)
        )
        chat_session = result.scalar_one_or_none()

        if not chat_session:
            # No chat history yet
            return ChatHistoryResponse(
                session_id=session_id,
                chat_session_id="",
                messages=[],
                summary=None,
                total_count=0,
                current_page=page,
                page_size=page_size,
                has_more=False
            )

        # Get total message count
        from sqlmodel import func
        count_result = await db_session.execute(
            select(func.count(ChatMessage.id))
            .where(ChatMessage.chat_session_id == chat_session.id)
        )
        total_count = count_result.scalar()

        # Calculate pagination
        offset = (page - 1) * page_size
        has_more = (offset + page_size) < total_count

        # Get messages for current page
        result = await db_session.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_session_id == chat_session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        messages = result.scalars().all()

        # Reverse to get chronological order
        messages = list(reversed(messages))

        # Format messages
        message_responses = [
            ChatMessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]

        # Get summary if available
        summary_text = None
        if total_count > 10:
            summary = await get_latest_chat_summary(
                chat_session_id=chat_session.id,
                db_session=db_session
            )
            if summary:
                summary_text = summary.summary_text

        return ChatHistoryResponse(
            session_id=session_id,
            chat_session_id=chat_session.chat_session_id,
            messages=message_responses,
            summary=summary_text,
            total_count=total_count,
            current_page=page,
            page_size=page_size,
            has_more=has_more
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to retrieve chat history: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving chat history: {str(e)}")


# =====================================================
# LifeSim Game Endpoints
# =====================================================

@app.post("/api/onboarding", response_model=OnboardingResponse, tags=["Game"])
async def create_player(
    request: OnboardingRequest,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new player profile and start the game

    This is the first endpoint called when starting a new game.

    **Supports:**
    - Authenticated users (with Authorization header) - links to account
    - Guest/test mode (no header) - creates anonymous session

    **Process:**
    1. Checks if user is authenticated (optional)
    2. Creates a player profile with provided information
    3. Links to account if authenticated (test_mode=False)
    4. Initializes game state with starting values
    5. Generates the first life event and decision options
    6. If first onboarding for account, saves as defaults
    7. Returns session_id for subsequent API calls

    **Returns:** Initial game state with narrative and decision options
    """
    try:
        # Check if authenticated (optional)
        account = None
        is_test_mode = True  # Default to test mode

        if authorization:
            # Try to get account - parse token
            parts = authorization.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
                account = await validate_token(token, session)
            else:
                account = None

            if account:
                is_test_mode = False  # Authenticated = not test mode
                print(
                    f"🔐 Authenticated user starting game: {account.username}")
            else:
                print(f"👤 Guest user starting game (test mode)")
        else:
            print(f"👤 Guest user starting game (test mode)")

        # Generate unique session ID
        session_id = generate_session_id()

        # Create player profile
        profile = PlayerProfile(
            session_id=session_id,
            player_name=request.player_name,
            account_id=account.id if account else None,
            is_test_mode=is_test_mode,
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

        # If authenticated and first onboarding, save as defaults
        if account and not account.has_completed_onboarding:
            account.default_age = request.age
            account.default_city = request.city
            account.default_education_path = request.education_path.value
            account.default_risk_attitude = request.risk_attitude.value
            account.default_monthly_income = request.monthly_income
            account.default_monthly_expenses = request.monthly_expenses
            account.default_starting_savings = request.starting_savings
            account.default_starting_debt = request.starting_debt
            account.default_aspirations = request.aspirations
            account.has_completed_onboarding = True
            print(
                f"✅ Saved onboarding defaults for account: {account.username}")

        # Initialize game state
        initial_state = initialize_game_state(
            profile, request.monthly_income, request.monthly_expenses)
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

        # Generate initial event and options
        initial_event_type = get_event_type(game_state, profile)

        initial_narrative = await generate_event_narrative(
            event_type=initial_event_type,
            state=game_state,
            profile=profile,
            db_session=session,
            curveball=None,
            client=client
        )

        # Generate dynamic options with AI - frontend will send these back with effects
        initial_options_data = generate_dynamic_options(
            event_type=initial_event_type,
            narrative=initial_narrative,
            state=game_state,
            profile=profile,
            client=client
        )

        game_state_response = GameStateResponse(
            session_id=session_id,
            current_step=game_state.current_step,
            current_age=game_state.current_age,
            years_passed=game_state.years_passed,
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
            initial_options=initial_options_data  # Return full option data with effects
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
            current_age=game_state.current_age,
            years_passed=game_state.years_passed,
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


@app.get("/api/transactions/{session_id}", response_model=List[dict], tags=["Game"])
async def get_transaction_logs(
    session_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get transaction history for a player session

    Retrieve all financial transactions made during the game for detailed tracking.
    Frontend can display these with color coding (green for gains, red for losses).

    **Parameters:**
    - **session_id**: Player's unique session identifier

    **Returns:** List of all transactions with changes and balances
    """
    try:
        # Find the profile
        result = await session.execute(
            select(PlayerProfile).where(PlayerProfile.session_id == session_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get all transaction logs
        result = await session.execute(
            select(TransactionLog)
            .where(TransactionLog.profile_id == profile.id)
            .order_by(TransactionLog.step_number)
        )
        transactions = result.scalars().all()

        return [
            {
                "step_number": t.step_number,
                "event_type": t.event_type,
                "chosen_option": t.chosen_option,
                "cash_change": t.cash_change,
                "investment_change": t.investment_change,
                "debt_change": t.debt_change,
                "monthly_income_change": t.monthly_income_change,
                "monthly_expense_change": t.monthly_expense_change,
                "passive_income_change": t.passive_income_change,
                "cash_balance": t.cash_balance,
                "investment_balance": t.investment_balance,
                "debt_balance": t.debt_balance,
                "monthly_income_total": t.monthly_income_total,
                "monthly_expense_total": t.monthly_expense_total,
                "passive_income_total": t.passive_income_total,
                "description": t.description,
                "created_at": t.created_at.isoformat()
            }
            for t in transactions
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving transaction logs: {str(e)}")


@app.get("/api/leaderboard", response_model=List[dict], tags=["Leaderboard"])
async def get_leaderboard(
    limit: int = 10,
    include_test_mode: bool = False,
    session: AsyncSession = Depends(get_session)
):
    """
    Get top players from the leaderboard

    Retrieve the highest-scoring players based on Financial Independence Score.
    By default, excludes test mode (guest) plays.

    **Parameters:**
    - **limit**: Maximum number of players to return (default: 10)
    - **include_test_mode**: Include test mode plays (default: false)

    **Returns:** List of top players with their scores and achievements
    """
    try:
        # Build query
        query = select(LeaderboardEntry).order_by(
            LeaderboardEntry.final_fi_score.desc())

        # Filter out test mode by default
        if not include_test_mode:
            query = query.where(LeaderboardEntry.is_test_mode == False)

        query = query.limit(limit)

        result = await session.execute(query)
        entries = result.scalars().all()

        return [
            {
                "rank": idx + 1,
                "player_name": entry.player_name,
                "final_fi_score": entry.final_fi_score,
                "balance_score": entry.balance_score,
                "age": entry.age,
                "education_path": entry.education_path,
                "completed_at": entry.completed_at.isoformat(),
                "is_test_mode": entry.is_test_mode
            }
            for idx, entry in enumerate(entries)
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving leaderboard: {str(e)}")


@app.get("/api/game/{session_id}/decisions", tags=["Game"])
async def get_decision_history(
    session_id: str,
    limit: Optional[int] = 10,
    db_session: AsyncSession = Depends(get_session)
):
    """
    Get decision history for a player session

    Retrieves the player's past decisions with before/after states.
    Includes automatic summarization if history exceeds 10 decisions.

    **Parameters:**
    - **session_id**: Player's session ID
    - **limit**: Maximum number of recent decisions to return (default: 10)

    **Returns:** Decision history with states, or summary + recent decisions
    """
    try:
        # Get player profile
        result = await db_session.execute(
            select(PlayerProfile).where(PlayerProfile.session_id == session_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get game state for current info
        result = await db_session.execute(
            select(GameState).where(GameState.profile_id == profile.id)
        )
        game_state = result.scalar_one_or_none()

        if not game_state:
            raise HTTPException(status_code=404, detail="Game state not found")

        # Get total count of decisions
        from sqlmodel import func
        count_result = await db_session.execute(
            select(func.count(DecisionHistory.id))
            .where(DecisionHistory.profile_id == profile.id)
        )
        total_decisions = count_result.scalar()

        # Get decision history
        from utils import get_recent_decisions, create_decision_summary

        decisions = await get_recent_decisions(
            profile_id=profile.id,
            db_session=db_session,
            limit=limit
        )

        # Format decisions for response
        decision_list = []
        for d in decisions:
            decision_list.append({
                "step": d.step_number,
                "event_type": d.event_type,
                "narrative": d.narrative,
                "chosen_option": d.chosen_option,
                "consequence": d.consequence_narrative,
                "learning_moment": d.learning_moment,
                "before": {
                    "fi_score": d.fi_score_before,
                    "money": d.money_before,
                    "energy": d.energy_before,
                    "motivation": d.motivation_before,
                    "social": d.social_before
                },
                "after": {
                    "fi_score": d.fi_score_after,
                    "money": d.money_after,
                    "energy": d.energy_after,
                    "motivation": d.motivation_after,
                    "social": d.social_after
                }
            })

        # Generate summary if needed
        summary = None
        if total_decisions > 10:
            # Get all decisions for summary
            all_result = await db_session.execute(
                select(DecisionHistory)
                .where(DecisionHistory.profile_id == profile.id)
                .order_by(DecisionHistory.step_number)
            )
            all_decisions = all_result.scalars().all()

            summary = await create_decision_summary(
                decisions=list(all_decisions),
                current_age=game_state.current_age,
                current_fi_score=game_state.fi_score
            )

        return {
            "session_id": session_id,
            "total_decisions": total_decisions,
            "decisions": decision_list,
            "summary": summary,
            "current_state": {
                "age": game_state.current_age,
                "fi_score": game_state.fi_score,
                "step": game_state.current_step
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to retrieve decision history: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


async def generate_and_cache_next_question(
    game_state_id: int,
    game_state: GameState,
    profile: PlayerProfile,
    db_session: AsyncSession,
    client: Optional[genai.Client]
):
    """
    Background task to generate and cache the next question/options.
    This runs asynchronously after the consequence is returned to the user.
    """
    try:
        import json
        from game_engine import get_event_type, generate_curveball_event, get_current_month_name
        from ai_narrative import generate_event_narrative, generate_dynamic_options

        print("\n🔄 Background: Starting next question generation...")

        # Generate next event
        next_event_type = get_event_type(game_state, profile)
        next_curveball = None
        if next_event_type == "curveball":
            next_curveball = generate_curveball_event(game_state)

        # Generate next narrative
        next_narrative = await generate_event_narrative(
            event_type=next_event_type,
            state=game_state,
            profile=profile,
            db_session=db_session,
            curveball=next_curveball,
            client=client
        )

        # Generate dynamic next options with AI
        next_options_data = generate_dynamic_options(
            event_type=next_event_type,
            narrative=next_narrative,
            state=game_state,
            profile=profile,
            client=client
        )

        # Add event context to each option for frontend to send back
        for opt in next_options_data:
            opt['event_type'] = next_event_type
            opt['narrative'] = next_narrative
            opt['all_options'] = [o['text'] for o in next_options_data]

        # Cache the results in the database
        # We need a new session since we're in a background task
        from database import async_engine
        from sqlalchemy.ext.asyncio import async_sessionmaker
        async_session = async_sessionmaker(
            async_engine, expire_on_commit=False)

        async with async_session() as new_db_session:
            # Fetch the game state again in this new session
            result = await new_db_session.execute(
                select(GameState).where(GameState.id == game_state_id)
            )
            cached_game_state = result.scalar_one_or_none()

            if cached_game_state:
                cached_game_state.cached_next_narrative = next_narrative
                cached_game_state.cached_next_options = json.dumps(
                    next_options_data)
                await new_db_session.commit()
                print("✅ Background: Next question cached successfully")
            else:
                print("⚠️ Background: Game state not found for caching")

    except Exception as e:
        print(f"❌ Background: Failed to generate next question: {e}")
        import traceback
        traceback.print_exc()


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
    - **chosen_option**: Text of chosen option
    - **option_index**: Index of the chosen decision option (0-based)

    **Returns:** Updated game state, consequence narrative, and next decision options
    """
    # === TIMING: Remove this line and all 'with timer()' blocks to disable ===
    start_total = time.time()

    try:
        # Get player profile and game state
        with timer("1. DB: Fetch profile and game state"):
            result = await db_session.execute(
                select(PlayerProfile).where(
                    PlayerProfile.session_id == request.session_id)
            )
            profile = result.scalar_one_or_none()

            if not profile:
                raise HTTPException(
                    status_code=404, detail="Session not found")

            result = await db_session.execute(
                select(GameState).where(GameState.profile_id == profile.id)
            )
            game_state = result.scalar_one_or_none()

            if not game_state:
                raise HTTPException(
                    status_code=404, detail="Game state not found")

            if game_state.game_status != GameStatus.ACTIVE:
                raise HTTPException(
                    status_code=400, detail="Game is not active")

        # Apply monthly cash flow (only on phase 1 - start of month)
        from game_engine import apply_monthly_cash_flow, get_month_phase_name, get_current_month_name

        with timer("2. Apply monthly cash flow"):
            cash_flow_data = apply_monthly_cash_flow(game_state)

        # Log the monthly cash flow as a transaction (only if applied)
        if cash_flow_data.get("applied", False):
            monthly_flow_log = TransactionLog(
                profile_id=profile.id,
                step_number=game_state.current_step,
                event_type="monthly_cash_flow",
                chosen_option=f"New month: {get_current_month_name(game_state.months_passed)}",
                cash_change=cash_flow_data["cash_change"],
                investment_change=0,
                debt_change=cash_flow_data["debt_from_deficit"],
                monthly_income_change=0,
                monthly_expense_change=0,
                passive_income_change=0,
                cash_balance=cash_flow_data["cash_balance"],
                investment_balance=game_state.investments,
                debt_balance=game_state.debts,
                monthly_income_total=game_state.monthly_income,
                monthly_expense_total=game_state.monthly_expenses,
                passive_income_total=game_state.passive_income,
                description=f"New month: Income €{cash_flow_data['income_received']:.0f} - Expenses €{cash_flow_data['expenses_paid']:.0f}"
            )
            db_session.add(monthly_flow_log)

        # Use the option data provided by the frontend
        if not request.option_effects:
            raise HTTPException(
                status_code=400,
                detail="option_effects is required. Frontend must send the full option data."
            )

        chosen_option_data = request.option_effects
        print(f"✅ Using frontend-provided option:")
        print(f"  Text: {chosen_option_data.get('text', 'N/A')[:80]}")
        print(
            f"  Risk level: {chosen_option_data.get('risk_level', 'unknown')}")
        print(f"  Category: {chosen_option_data.get('category', 'unknown')}")

        # Extract event info from option data (for logging)
        current_event_type = chosen_option_data.get('event_type', 'unknown')
        current_narrative = chosen_option_data.get(
            'narrative', request.chosen_option)

        # Store state BEFORE any changes
        state_before = {
            'money': game_state.money,
            'investments': game_state.investments,
            'fi_score': game_state.fi_score,
            'energy': game_state.energy,
            'motivation': game_state.motivation,
            'social': game_state.social_life,
            'knowledge': game_state.financial_knowledge
        }
        step_number = game_state.current_step

        # Generate consequence narrative AND effects (AI determines what happens)
        print(
            f"\n🎲 Generating consequence with AI (risk level: {chosen_option_data.get('risk_level', 'unknown')})...")
        consequence_result = await generate_consequence_narrative(
            chosen_option=request.chosen_option,
            option_data=chosen_option_data,
            state=game_state,
            profile=profile,
            event_narrative=current_narrative,
            state_before=state_before,
            db_session=db_session,
            client=client
        )

        consequence = consequence_result['narrative']
        effects_dict = consequence_result['effects']

        print(f"📜 Consequence: {consequence[:100]}...")
        print(f"💰 Effects from AI:")
        print(f"  Money: {effects_dict.get('money_change', 0)}")
        print(f"  Investments: {effects_dict.get('investment_change', 0)}")
        print(f"  Debt: {effects_dict.get('debt_change', 0)}")

        # NOW apply the effects that the AI determined
        effect = setup_dynamic_option_effect(effects_dict)
        transaction_data = apply_decision_effects(game_state, effect)

        print(
            f"  After effects - Money: {game_state.money}, Investments: {game_state.investments}")

        # Calculate life metrics changes
        life_metrics_changes = LifeMetricsChanges(
            energy_change=game_state.energy - state_before['energy'],
            motivation_change=game_state.motivation -
            state_before['motivation'],
            social_change=game_state.social_life - state_before['social'],
            knowledge_change=game_state.financial_knowledge -
            state_before['knowledge']
        )

        # Generate learning moment (sometimes)
        with timer("8. AI: Generate learning moment"):
            learning = generate_learning_moment(
                chosen_option=request.chosen_option,
                state=game_state,
                profile=profile,
                client=client
            )

        # For options_presented, use what frontend sent (if available)
        options_presented_texts = chosen_option_data.get(
            'all_options', [request.chosen_option])

        # Record decision in history
        decision_record = DecisionHistory(
            profile_id=profile.id,
            step_number=step_number,
            event_type=current_event_type,
            narrative=current_narrative,
            options_presented=options_presented_texts,
            chosen_option=request.chosen_option,
            money_before=state_before['money'],
            fi_score_before=state_before['fi_score'],
            energy_before=state_before['energy'],
            motivation_before=state_before['motivation'],
            social_before=state_before['social'],
            money_after=game_state.money,
            fi_score_after=game_state.fi_score,
            energy_after=game_state.energy,
            motivation_after=game_state.motivation,
            social_after=game_state.social_life,
            consequence_narrative=consequence,
            learning_moment=learning
        )

        db_session.add(decision_record)

        # Create transaction log entry
        transaction_log = TransactionLog(
            profile_id=profile.id,
            step_number=step_number,
            event_type=current_event_type,
            chosen_option=request.chosen_option,
            cash_change=transaction_data["cash_change"],
            investment_change=transaction_data["investment_change"],
            debt_change=transaction_data["debt_change"],
            monthly_income_change=transaction_data["monthly_income_change"],
            monthly_expense_change=transaction_data["monthly_expense_change"],
            passive_income_change=transaction_data["passive_income_change"],
            cash_balance=transaction_data["cash_balance"],
            investment_balance=transaction_data["investment_balance"],
            debt_balance=transaction_data["debt_balance"],
            monthly_income_total=transaction_data["monthly_income_total"],
            monthly_expense_total=transaction_data["monthly_expense_total"],
            passive_income_total=transaction_data["passive_income_total"],
            description=transaction_data["description"]
        )

        db_session.add(transaction_log)

        # Update game state in database
        with timer("9. DB: Commit and refresh"):
            await db_session.commit()
            await db_session.refresh(game_state)

        # Build updated state response
        updated_state = GameStateResponse(
            session_id=request.session_id,
            current_step=game_state.current_step,
            current_age=game_state.current_age,
            years_passed=game_state.years_passed,
            months_passed=game_state.months_passed,
            month_phase=game_state.month_phase,
            money=game_state.money,
            monthly_income=game_state.monthly_income,
            monthly_expenses=game_state.monthly_expenses,
            expense_housing=game_state.expense_housing,
            expense_food=game_state.expense_food,
            expense_transport=game_state.expense_transport,
            expense_utilities=game_state.expense_utilities,
            expense_subscriptions=game_state.expense_subscriptions,
            expense_insurance=game_state.expense_insurance,
            expense_other=game_state.expense_other,
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

        # Create timestamp for transaction
        month_name = get_current_month_name(game_state.months_passed)
        phase_name = get_month_phase_name(game_state.month_phase)
        timestamp = f"{phase_name} {month_name[:3]}"  # e.g., "Early Jan"

        # Create transaction summary for the player's decision
        transaction_summary = TransactionSummary(
            cash_change=transaction_data["cash_change"],
            investment_change=transaction_data["investment_change"],
            debt_change=transaction_data["debt_change"],
            monthly_income_change=transaction_data["monthly_income_change"],
            monthly_expense_change=transaction_data["monthly_expense_change"],
            passive_income_change=transaction_data["passive_income_change"],
            expense_housing_change=transaction_data.get(
                "expense_housing_change", 0.0),
            expense_food_change=transaction_data.get(
                "expense_food_change", 0.0),
            expense_transport_change=transaction_data.get(
                "expense_transport_change", 0.0),
            expense_utilities_change=transaction_data.get(
                "expense_utilities_change", 0.0),
            expense_subscriptions_change=transaction_data.get(
                "expense_subscriptions_change", 0.0),
            expense_insurance_change=transaction_data.get(
                "expense_insurance_change", 0.0),
            expense_other_change=transaction_data.get(
                "expense_other_change", 0.0),
            cash_balance=transaction_data["cash_balance"],
            investment_balance=transaction_data["investment_balance"],
            debt_balance=transaction_data["debt_balance"],
            monthly_income_total=transaction_data["monthly_income_total"],
            monthly_expense_total=transaction_data["monthly_expense_total"],
            passive_income_total=transaction_data["passive_income_total"],
            description=transaction_data["description"],
            timestamp=timestamp
        )

        # Create monthly cash flow transaction (if applied this step)
        monthly_flow_transaction = None
        if cash_flow_data.get("applied", False):
            monthly_flow_transaction = TransactionSummary(
                cash_change=cash_flow_data["cash_change"],
                investment_change=0.0,
                debt_change=cash_flow_data.get("debt_from_deficit", 0.0),
                monthly_income_change=0.0,
                monthly_expense_change=0.0,
                passive_income_change=0.0,
                cash_balance=cash_flow_data["cash_balance"],
                investment_balance=game_state.investments,
                debt_balance=game_state.debts,
                monthly_income_total=game_state.monthly_income,
                monthly_expense_total=game_state.monthly_expenses,
                passive_income_total=game_state.passive_income,
                description=f"New month: Income €{cash_flow_data['income_received']:.0f} - Expenses €{cash_flow_data['expenses_paid']:.0f}",
                timestamp=timestamp
            )

        # Create monthly cash flow summary for response
        monthly_cash_flow_summary = MonthlyCashFlowSummary(
            applied=cash_flow_data.get("applied", False),
            income_received=cash_flow_data.get("income_received", 0.0),
            expenses_paid=cash_flow_data.get("expenses_paid", 0.0),
            net_change=cash_flow_data.get("cash_change", 0.0),
            debt_from_deficit=cash_flow_data.get("debt_from_deficit", 0.0),
            month_name=get_current_month_name(game_state.months_passed),
            month_phase=game_state.month_phase,
            month_phase_name=get_month_phase_name(game_state.month_phase)
        )

        # === TIMING: Print time before next question generation ===
        time_before_next = time.time() - start_total
        print(
            f"\n⏱️  Time to consequence (before next Q): {time_before_next:.3f}s\n")

        # Start background task to generate next question
        import asyncio
        asyncio.create_task(
            generate_and_cache_next_question(
                game_state.id,
                game_state,
                profile,
                db_session,
                client
            )
        )

        # Return consequence immediately (next question will be cached)
        return DecisionResponse(
            consequence_narrative=consequence,
            updated_state=updated_state,
            next_narrative=None,  # Will be fetched separately
            next_options=None,  # Will be fetched separately
            learning_moment=learning,
            transaction_summary=transaction_summary,
            monthly_flow_transaction=monthly_flow_transaction,
            monthly_cash_flow=monthly_cash_flow_summary,
            life_metrics_changes=life_metrics_changes,
            is_generating_next=True
        )

    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing decision: {str(e)}")


@app.get("/api/next-question/{session_id}", tags=["Game"])
async def get_next_question(
    session_id: str,
    db_session: AsyncSession = Depends(get_session)
):
    """
    Fetch the pre-generated next question and options.
    This is called after showing the consequence to get the cached next question.

    Returns the cached narrative and options if available, otherwise generates them on-demand.
    """
    try:
        import json

        # Get profile and game state
        result = await db_session.execute(
            select(PlayerProfile).where(PlayerProfile.session_id == session_id)
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

        # Check if we have a cached question
        if game_state.cached_next_narrative and game_state.cached_next_options:
            print("✅ Returning cached next question")
            next_narrative = game_state.cached_next_narrative
            next_options = json.loads(game_state.cached_next_options)

            # Clear the cache after retrieving
            game_state.cached_next_narrative = None
            game_state.cached_next_options = None
            await db_session.commit()

            return {
                "next_narrative": next_narrative,
                "next_options": next_options,
                "was_cached": True
            }

        # If not cached, generate on-demand
        print("⚠️ Cache miss - generating next question on-demand")
        client = get_ai_client()

        next_event_type = get_event_type(game_state, profile)
        next_curveball = None
        if next_event_type == "curveball":
            next_curveball = generate_curveball_event(game_state)

        next_narrative = await generate_event_narrative(
            event_type=next_event_type,
            state=game_state,
            profile=profile,
            db_session=db_session,
            curveball=next_curveball,
            client=client
        )

        next_options_data = generate_dynamic_options(
            event_type=next_event_type,
            narrative=next_narrative,
            state=game_state,
            profile=profile,
            client=client
        )

        # Add event context to each option
        for opt in next_options_data:
            opt['event_type'] = next_event_type
            opt['narrative'] = next_narrative
            opt['all_options'] = [o['text'] for o in next_options_data]

        return {
            "next_narrative": next_narrative,
            "next_options": next_options_data,
            "was_cached": False
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get next question: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# LEADERBOARD ENDPOINTS
# ===========================
