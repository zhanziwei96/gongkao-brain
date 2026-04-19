from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from uuid import UUID


class UserBase(BaseModel):
    username: str
    email: str
    exam_type: Optional[str] = "国考副省级"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AptitudeQuestionBase(BaseModel):
    source_exam: Optional[str] = "国考副省级"
    question_type: str
    question_text: Optional[str] = None
    question_image_url: Optional[str] = None
    question_pdf_url: Optional[str] = None
    options: Optional[Dict[str, str]] = None
    correct_answer: Optional[str] = None
    difficulty: Optional[int] = 3


class AptitudeQuestionCreate(AptitudeQuestionBase):
    pass


class AptitudeQuestionResponse(AptitudeQuestionBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AptitudeQuestionList(BaseModel):
    items: List[AptitudeQuestionResponse]
    total: int


class AptitudeAttemptBase(BaseModel):
    user_answer: str
    time_spent_seconds: Optional[int] = None


class AptitudeAttemptCreate(AptitudeAttemptBase):
    question_id: UUID


class AptitudeAttemptResponse(AptitudeAttemptBase):
    id: UUID
    user_id: UUID
    question_id: UUID
    is_correct: Optional[bool]
    is_mistake: bool
    attempt_date: datetime

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[Dict[str, Any]] = None


class ChatStreamResponse(BaseModel):
    delta: str
    done: bool = False
