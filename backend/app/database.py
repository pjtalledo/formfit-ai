from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DB_PATH

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class AthleteProfile(Base):
    __tablename__ = "athlete_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    experience_level = Column(String, nullable=False)
    goals = Column(String, nullable=False)
    equipment = Column(JSON, nullable=False, default=list)
    limitations = Column(String, nullable=True, default="")
    weight_unit = Column(String, nullable=False, default="lb")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class WorkoutResult(Base):
    __tablename__ = "workout_results"

    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, nullable=False, index=True)
    source = Column(String, nullable=False)  # "typed" or "image"
    raw_input = Column(String, nullable=False)
    parsed_wod = Column(JSON, nullable=False)
    recommendation = Column(JSON, nullable=False)
    model_used = Column(String, nullable=False)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    cached_tokens = Column(Integer, nullable=True)
    estimated_cost_usd = Column(Float, nullable=True)
    agent_trace = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
