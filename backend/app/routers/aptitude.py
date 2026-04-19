import os
import uuid
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.dependencies import get_current_user
from app.models import AptitudeQuestion, AptitudeAttempt, User
from app.schemas import (
    AptitudeQuestionCreate, AptitudeQuestionResponse, AptitudeQuestionList,
    AptitudeAttemptCreate, AptitudeAttemptResponse, AptitudeStats
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
    if is_mistake is not None:
        # 先查出有/无错题记录的 question_id 列表
        mistake_question_ids = db.query(AptitudeAttempt.question_id).filter(
            AptitudeAttempt.user_id == current_user.id,
            AptitudeAttempt.is_mistake == True
        ).distinct().all()
        mistake_ids = [row[0] for row in mistake_question_ids]

        if is_mistake:
            # 只看错题
            query = query.filter(AptitudeQuestion.id.in_(mistake_ids))
        else:
            # 只看非错题（包括未作答的）
            query = query.filter(~AptitudeQuestion.id.in_(mistake_ids))
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


@router.get("/stats", response_model=AptitudeStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 总题目数
    total_questions = db.query(AptitudeQuestion).filter(
        AptitudeQuestion.user_id == current_user.id
    ).count()

    # 答题记录统计
    attempts = db.query(AptitudeAttempt).filter(
        AptitudeAttempt.user_id == current_user.id
    )
    total_attempts = attempts.count()
    correct_count = attempts.filter(AptitudeAttempt.is_correct == True).count()
    mistake_count = attempts.filter(AptitudeAttempt.is_mistake == True).count()

    # 正确率（基于有答题记录的题目）
    accuracy_rate = round(correct_count / total_attempts * 100) if total_attempts > 0 else 0

    # 各模块统计：按题型分组，统计每类的答题数和正确数
    question_types = ['政治理论', '常识判断', '言语理解', '数量关系', '判断推理', '资料分析']
    module_stats = []

    for qt in question_types:
        # 该题型的题目数量
        q_count = db.query(AptitudeQuestion).filter(
            AptitudeQuestion.user_id == current_user.id,
            AptitudeQuestion.question_type == qt
        ).count()

        # 该题型的答题记录
        mod_attempts = db.query(AptitudeAttempt).join(AptitudeQuestion).filter(
            AptitudeAttempt.user_id == current_user.id,
            AptitudeQuestion.question_type == qt
        )
        mod_total = mod_attempts.count()
        mod_correct = mod_attempts.filter(AptitudeAttempt.is_correct == True).count()
        mod_rate = round(mod_correct / mod_total * 100) if mod_total > 0 else 0

        module_stats.append({
            "name": qt,
            "question_count": q_count,
            "attempt_count": mod_total,
            "correct_count": mod_correct,
            "rate": mod_rate
        })

    return {
        "total_questions": total_questions,
        "total_attempts": total_attempts,
        "correct_count": correct_count,
        "mistake_count": mistake_count,
        "accuracy_rate": accuracy_rate,
        "module_stats": module_stats
    }
