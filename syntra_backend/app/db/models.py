from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base
import enum

# ─── Enums ────────────────────────────────────────────────────────────────────

class FeatureNameEnum(str, enum.Enum):
    enhance = "enhance"
    intent = "intent"
    compress = "compress"
    chat = "chat"

# ─── Existing Tables ──────────────────────────────────────────────────────────

class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(255), index=True)
    request_payload = Column(Text, nullable=True)
    response_status = Column(Integer)
    processing_time_ms = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    workspaces = relationship("Workspace", back_populates="user", cascade="all, delete-orphan")
    usage_metrics = relationship("UsageMetric", back_populates="user", cascade="all, delete-orphan")

# ─── New Tables ───────────────────────────────────────────────────────────────

class Workspace(Base):
    """Groups a user's ChatSessions into named projects."""
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    user = relationship("User", back_populates="workspaces")
    sessions = relationship("ChatSession", back_populates="workspace", cascade="all, delete-orphan")


class ChatSession(Base):
    """A named session of work inside a Workspace."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    session_name = Column(String(255), nullable=False, default="Untitled Session")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    workspace = relationship("Workspace", back_populates="sessions")
    history_items = relationship("FeatureHistory", back_populates="session", cascade="all, delete-orphan")


class FeatureHistory(Base):
    """Stores a single input/output pair for any of the 4 Syntra features."""
    __tablename__ = "feature_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_name = Column(Enum(FeatureNameEnum), nullable=False, index=True)
    input_prompt = Column(Text, nullable=False)
    output_data = Column(Text, nullable=False)   # JSON stored as Text (Supabase free tier compatible)
    model_used = Column(String(100), nullable=True)  # e.g. "gemini-2.0-flash", "llama-3.3-70b"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    session = relationship("ChatSession", back_populates="history_items")


class UsageMetric(Base):
    """Tracks background LLM token usage per user per request."""
    __tablename__ = "usage_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # nullable for anonymous
    feature_name = Column(Enum(FeatureNameEnum), nullable=False)
    provider = Column(String(100), nullable=False)  # "gemini", "openrouter", "groq"
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    user = relationship("User", back_populates="usage_metrics")

