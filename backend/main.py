from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from google import genai
from sqlmodel import Session

# Import database setup
from database import create_db_and_tables, get_session
from models import User, ChatHistory

load_dotenv()

app = FastAPI(title="AI Hackathon API")

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


@app.get("/")
async def root():
    return {"message": "AI Hackathon API is running!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage, session: Session = Depends(get_session)):
    """
    Basic chat endpoint - integrate with OpenAI, Anthropic, or other LLM providers
    """
    try:
        if not GEMINI_API_KEY or not client:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Map of valid Gemini models
        valid_models = ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
        
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
        
        # Save chat history to database
        chat_history = ChatHistory(
            message=chat_message.message,
            response=response.text,
            model=model_to_use
        )
        session.add(chat_history)
        session.commit()
        
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
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.get("/api/models")
async def list_models():
    """
    List available models
    """
    return {
        "models": [
            {"id": "gemini-2.0-flash-exp", "name": "Gemini 2.0 Flash (Experimental)"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
            {"id": "gemini-pro", "name": "Gemini Pro"},
        ]
    }


# Example endpoints using SQLModel

@app.post("/api/users", response_model=User)
async def create_user(user: User, session: Session = Depends(get_session)):
    """Create a new user"""
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    """Get a user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/api/chat/history")
async def get_chat_history(session: Session = Depends(get_session), limit: int = 10):
    """Get recent chat history"""
    from sqlmodel import select
    statement = select(ChatHistory).order_by(ChatHistory.created_at.desc()).limit(limit)
    chats = session.exec(statement).all()
    return {"history": chats}
