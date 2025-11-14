from sqlmodel import SQLModel, create_engine, Session
import os

# SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
