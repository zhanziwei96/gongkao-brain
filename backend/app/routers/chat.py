from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import ChatRequest
from app.services.ai_service import stream_claude_response

router = APIRouter()


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    context = request.context or {}
    context["user"] = current_user.username

    async def event_generator():
        async for chunk in stream_claude_response(messages, context):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
