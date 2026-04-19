from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, aptitude, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="公考大脑 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(aptitude.router, prefix="/api/aptitude", tags=["行测"])
app.include_router(chat.router, prefix="/api/chat", tags=["聊天"])


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
