import os
import uuid
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import AptitudeQuestion, AptitudeAttempt, User
from app.schemas import (
    AptitudeQuestionCreate, AptitudeQuestionResponse, AptitudeQuestionList,
    AptitudeAttemptCreate, AptitudeAttemptResponse
)

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "aptitude")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".webp"]:
        raise HTTPException(status_code=400, detail="仅支持图片或 PDF 格式")

    file_id = str(uuid.uuid4())
    filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return {"url": f"/uploads/aptitude/{filename}"}


@router.post("/parse")
async def parse_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传图片/PDF，调用AI解析题目内容"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".webp"]:
        raise HTTPException(status_code=400, detail="仅支持图片或 PDF 格式")

    file_id = str(uuid.uuid4())
    filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    try:
        from app.services.ocr_service import parse_image, parse_pdf
        if ext == ".pdf":
            result = await parse_pdf(file_path)
        else:
            result = await parse_image(file_path)
        result["file_url"] = f"/uploads/aptitude/{filename}"
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.post("/questions", response_model=AptitudeQuestionResponse)
def create_question(
    data: AptitudeQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = AptitudeQuestion(
        user_id=current_user.id,
        source_exam=data.source_exam,
        question_type=data.question_type,
        question_text=data.question_text,
        question_image_url=data.question_image_url,
        options=data.options,
        correct_answer=data.correct_answer,
        difficulty=data.difficulty
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.get("/questions", response_model=AptitudeQuestionList)
def list_questions(
    question_type: Optional[str] = None,
    is_mistake: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(AptitudeQuestion).filter(AptitudeQuestion.user_id == current_user.id)
    if question_type:
        query = query.filter(AptitudeQuestion.question_type == question_type)
    total = query.count()
    items = query.order_by(AptitudeQuestion.created_at.desc()).offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.get("/questions/{question_id}", response_model=AptitudeQuestionResponse)
def get_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(AptitudeQuestion).filter(
        AptitudeQuestion.id == question_id,
        AptitudeQuestion.user_id == current_user.id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/questions/{question_id}", response_model=AptitudeQuestionResponse)
def update_question(
    question_id: UUID,
    data: AptitudeQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(AptitudeQuestion).filter(
        AptitudeQuestion.id == question_id,
        AptitudeQuestion.user_id == current_user.id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    for field, value in data.model_dump().items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)
    return question


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(AptitudeQuestion).filter(
        AptitudeQuestion.id == question_id,
        AptitudeQuestion.user_id == current_user.id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(question)
    db.commit()
    return {"message": "Question deleted"}


@router.post("/attempts", response_model=AptitudeAttemptResponse)
def create_attempt(
    data: AptitudeAttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(AptitudeQuestion).filter(
        AptitudeQuestion.id == data.question_id,
        AptitudeQuestion.user_id == current_user.id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    is_correct = question.correct_answer == data.user_answer if question.correct_answer else None
    is_mistake = is_correct is False

    attempt = AptitudeAttempt(
        user_id=current_user.id,
        question_id=data.question_id,
        user_answer=data.user_answer,
        is_correct=is_correct,
        time_spent_seconds=data.time_spent_seconds,
        is_mistake=is_mistake
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


@router.get("/attempts", response_model=List[AptitudeAttemptResponse])
def list_attempts(
    question_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(AptitudeAttempt).filter(AptitudeAttempt.user_id == current_user.id)
    if question_id:
        query = query.filter(AptitudeAttempt.question_id == question_id)
    return query.order_by(AptitudeAttempt.attempt_date.desc()).all()
