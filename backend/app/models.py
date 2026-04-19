import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    exam_type = Column(String(20), default="国考副省级")
    created_at = Column(DateTime, default=datetime.utcnow)

    aptitude_questions = relationship("AptitudeQuestion", back_populates="user", cascade="all, delete-orphan")
    aptitude_attempts = relationship("AptitudeAttempt", back_populates="user", cascade="all, delete-orphan")


class AptitudeQuestion(Base):
    __tablename__ = "aptitude_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    source_exam = Column(String(20), default="国考副省级")
    question_type = Column(String(20), nullable=False)
    question_text = Column(Text)
    question_image_url = Column(String(500))
    options = Column(JSON, default=dict)
    correct_answer = Column(String(10))
    difficulty = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="aptitude_questions")
    attempts = relationship("AptitudeAttempt", back_populates="question", cascade="all, delete-orphan")


class AptitudeAttempt(Base):
    __tablename__ = "aptitude_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("aptitude_questions.id"), nullable=False)
    user_answer = Column(String(10))
    is_correct = Column(Boolean)
    time_spent_seconds = Column(Integer)
    attempt_date = Column(DateTime, default=datetime.utcnow)
    is_mistake = Column(Boolean, default=False)

    user = relationship("User", back_populates="aptitude_attempts")
    question = relationship("AptitudeQuestion", back_populates="attempts")
