# backend/storage.py
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Float,
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./promptshield.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class AttackLog(Base):
    __tablename__ = "attack_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    raw_prompt = Column(Text)
    sanitized_prompt = Column(Text)
    wrapped_prompt = Column(Text)

    action = Column(String(20))  # pass | sanitize | block
    regex_score = Column(Integer)
    entropy_score = Column(Integer)
    anomaly_score = Column(Integer)
    total_score = Column(Integer)

    ppa_template_id = Column(String(50))
    processing_ms = Column(Float)


def init_db():
    Base.metadata.create_all(bind=engine)
