# P0 核心基础设施与行测错题管理 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建项目基础架构（Docker Compose + PostgreSQL/pgvector + Redis + MinIO），实现用户认证、行测错题CRUD、基础AI聊天面板，产出可运行的Web应用。

**Architecture:** 前后端分离架构。前端Vue3+Vite+Element Plus，后端Python FastAPI+SQLAlchemy+Alembic，数据层PostgreSQL+pgvector，文件存储MinIO，异步任务Celery+Redis（本期仅配置，不实现复杂任务）。AI对话通过FastAPI SSE代理Claude API。

**Tech Stack:** Vue3, Vite, Element Plus, TypeScript, Pinia, Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, pgvector, Redis, MinIO, Celery, Pytest, JWT, Claude API

---

## 文件结构

```
gongkao-brain/
├── frontend/                    # Vue3 前端
│   ├── src/
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── AptitudeQuestionList.vue
│   │   │   ├── AptitudeQuestionForm.vue
│   │   │   └── ChatPanel.vue
│   │   ├── components/
│   │   │   ├── NavigationMenu.vue
│   │   │   └── ChatMessage.vue
│   │   ├── stores/
│   │   │   ├── auth.ts
│   │   │   ├── chat.ts
│   │   │   └── aptitude.ts
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── auth.ts
│   │   │   ├── aptitude.ts
│   │   │   └── chat.ts
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── aptitude.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   └── ai_service.py
│   │   └── dependencies.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_aptitude.py
│   │   └── test_chat.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   └── alembic/
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Task 1: 项目初始化与 Git 仓库

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `.env.example`

- [ ] **Step 1: 初始化 Git 仓库**

```bash
cd /home/yufeng/gongkao-brain
git init
git checkout -b main
```

- [ ] **Step 2: 创建根目录 .gitignore**

```bash
cat > /home/yufeng/gongkao-brain/.gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
venv/
.env

# Node
node_modules/
dist/
*.log
npm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
postgres_data/
redis_data/
minio_data/
EOF
```

- [ ] **Step 3: 创建 README.md**

```bash
cat > /home/yufeng/gongkao-brain/README.md << 'EOF'
# 公考大脑 (Gongkao Brain)

智能化公务员考试备考系统，集成 Graphify 知识图谱与 Karpathy Wiki 知识管理。

## 快速开始

```bash
# 复制环境变量
cp .env.example .env
# 编辑 .env 填入你的 CLAUDE_API_KEY

# 启动所有服务
docker-compose up -d

# 前端开发
cd frontend && npm install && npm run dev

# 后端开发
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
```

## 技术栈

- 前端: Vue3 + Vite + Element Plus + TypeScript
- 后端: Python + FastAPI + SQLAlchemy + Alembic
- 数据库: PostgreSQL + pgvector
- 缓存/队列: Redis + Celery
- 文件存储: MinIO
EOF
```

- [ ] **Step 4: 创建 .env.example**

```bash
cat > /home/yufeng/gongkao-brain/.env.example << 'EOF'
# Database
DATABASE_URL=postgresql://gongkao:gongkao_pass@localhost:5432/gongkao

# Redis
REDIS_URL=redis://localhost:6379/0

# AI API
CLAUDE_API_KEY=sk-your-claude-api-key
CLAUDE_MODEL=claude-sonnet-4-6

# File Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=gongkao

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Graphify
GRAPHIFY_CONFIG_PATH=./graphify/config.yaml
EOF
```

- [ ] **Step 5: Commit**

```bash
cd /home/yufeng/gongkao-brain
git add .gitignore README.md .env.example
git commit -m "chore: project init with gitignore, readme, env template

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: Docker Compose 编排

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: 创建 docker-compose.yml**

```bash
cat > /home/yufeng/gongkao-brain/docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: ankane/pgvector:latest
    container_name: gongkao-db
    environment:
      POSTGRES_USER: gongkao
      POSTGRES_PASSWORD: gongkao_pass
      POSTGRES_DB: gongkao
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U gongkao"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: gongkao-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio:latest
    container_name: gongkao-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  redis_data:
  minio_data:
EOF
```

- [ ] **Step 2: 启动基础设施**

```bash
cd /home/yufeng/gongkao-brain
docker-compose up -d
```

Expected output:
```
[+] Running 4/4
 ✔ Network gongkao-brain_default  Created
 ✔ Container gongkao-db          Started
 ✔ Container gongkao-redis       Started
 ✔ Container gongkao-minio       Started
```

- [ ] **Step 3: 验证数据库**

```bash
docker exec gongkao-db pg_isready -U gongkao
```

Expected output: `/var/run/postgresql:5432 - accepting connections`

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml
git commit -m "chore: add docker-compose for postgres, redis, minio

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: 后端基础架构

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/models.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: 创建 requirements.txt**

```bash
mkdir -p /home/yufeng/gongkao-brain/backend/app/routers
mkdir -p /home/yufeng/gongkao-brain/backend/app/services
mkdir -p /home/yufeng/gongkao-brain/backend/alembic/versions
mkdir -p /home/yufeng/gongkao-brain/backend/tests

cat > /home/yufeng/gongkao-brain/backend/requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
alembic==1.14.0
psycopg2-binary==2.9.10
pgvector==0.3.6
redis==5.2.0
celery==5.4.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.17
httpx==0.27.2
pydantic==2.9.2
pydantic-settings==2.6.1
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
EOF
```

- [ ] **Step 2: 创建 Dockerfile**

```bash
cat > /home/yufeng/gongkao-brain/backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

- [ ] **Step 3: 创建配置模块**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/config.py << 'EOF'
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://gongkao:gongkao_pass@localhost:5432/gongkao"
    redis_url: str = "redis://localhost:6379/0"
    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"
    jwt_secret_key: str = "dev-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "gongkao"

    class Config:
        env_file = ".env"


settings = Settings()
EOF
```

- [ ] **Step 4: 创建数据库模块**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF
```

- [ ] **Step 5: 创建基础模型**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/models.py << 'EOF'
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


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
EOF
```

- [ ] **Step 6: 创建 Pydantic schemas**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/schemas.py << 'EOF'
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from uuid import UUID


# User schemas
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


# Aptitude Question schemas
class AptitudeQuestionBase(BaseModel):
    source_exam: Optional[str] = "国考副省级"
    question_type: str
    question_text: Optional[str] = None
    question_image_url: Optional[str] = None
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


# Aptitude Attempt schemas
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


# Chat schemas
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[Dict[str, Any]] = None


class ChatStreamResponse(BaseModel):
    delta: str
    done: bool = False
EOF
```

- [ ] **Step 7: 创建 alembic.ini**

```bash
cat > /home/yufeng/gongkao-brain/backend/alembic.ini << 'EOF'
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://gongkao:gongkao_pass@localhost:5432/gongkao

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF
```

- [ ] **Step 8: 创建 alembic/env.py**

```bash
cat > /home/yufeng/gongkao-brain/backend/alembic/env.py << 'EOF'
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.models import User, AptitudeQuestion, AptitudeAttempt

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF
```

- [ ] **Step 9: 创建 alembic/script.py.mako**

```bash
cat > /home/yufeng/gongkao-brain/backend/alembic/script.py.mako << 'EOF'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
EOF
```

- [ ] **Step 10: 创建入口 main.py**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/main.py << 'EOF'
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
EOF
```

- [ ] **Step 11: 安装依赖并创建初始迁移**

```bash
cd /home/yufeng/gongkao-brain/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Expected output: Successfully installed all packages.

```bash
cd /home/yufeng/gongkao-brain/backend
alembic revision --autogenerate -m "init users and aptitude tables"
alembic upgrade head
```

Expected output: `INFO  [alembic.runtime.migration] Running upgrade  -> <revision>, init users and aptitude tables`

- [ ] **Step 12: Commit**

```bash
git add backend/
git commit -m "feat: backend foundation with FastAPI, SQLAlchemy, Alembic, models

- Add User, AptitudeQuestion, AptitudeAttempt models
- Add Pydantic schemas
- Add Docker Compose for postgres, redis, minio
- Add initial Alembic migration

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: 用户认证系统

**Files:**
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/dependencies.py`
- Create: `backend/app/routers/auth.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: 创建认证服务**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/services/auth_service.py << 'EOF'
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import User
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, email: str, password: str) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
EOF
```

- [ ] **Step 2: 创建依赖模块**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/dependencies.py << 'EOF'
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import decode_token
from app.models import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
EOF
```

- [ ] **Step 3: 创建认证路由**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/routers/auth.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserResponse, UserLogin, Token
from app.services.auth_service import create_user, authenticate_user, create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    from app.services.auth_service import get_user_by_username
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    user = create_user(db, user_data.username, user_data.email, user_data.password)
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
EOF
```

- [ ] **Step 4: 创建测试配置**

```bash
cat > /home/yufeng/gongkao-brain/backend/tests/conftest.py << 'EOF'
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient

TEST_DATABASE_URL = "postgresql://gongkao:gongkao_pass@localhost:5432/gongkao_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
EOF
```

- [ ] **Step 5: 创建认证测试**

```bash
cat > /home/yufeng/gongkao-brain/backend/tests/test_auth.py << 'EOF'
def test_register_success(client):
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_duplicate_username(client):
    client.post("/api/auth/register", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpass123"
    })
    response = client.post("/api/auth/register", json={
        "username": "testuser2",
        "email": "test3@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client):
    client.post("/api/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "loginpass123"
    })
    response = client.post("/api/auth/login", json={
        "username": "loginuser",
        "password": "loginpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "wrongpass"
    })
    assert response.status_code == 401
EOF
```

- [ ] **Step 6: 运行测试**

```bash
cd /home/yufeng/gongkao-brain/backend
source venv/bin/activate
pytest tests/test_auth.py -v
```

Expected output: 4 tests passed.

- [ ] **Step 7: Commit**

```bash
git add backend/app/services/auth_service.py backend/app/dependencies.py backend/app/routers/auth.py backend/tests/
git commit -m "feat: add JWT authentication system with tests

- Add register/login endpoints
- Add password hashing with bcrypt
- Add JWT token creation and validation
- Add get_current_user dependency
- Add auth tests

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: 行测题目 CRUD API

**Files:**
- Create: `backend/app/routers/aptitude.py`
- Create: `backend/tests/test_aptitude.py`

- [ ] **Step 1: 创建行测路由**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/routers/aptitude.py << 'EOF'
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import AptitudeQuestion, AptitudeAttempt, User
from app.schemas import (
    AptitudeQuestionCreate, AptitudeQuestionResponse, AptitudeQuestionList,
    AptitudeAttemptCreate, AptitudeAttemptResponse
)

router = APIRouter()


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
EOF
```

- [ ] **Step 2: 创建行测测试**

```bash
cat > /home/yufeng/gongkao-brain/backend/tests/test_aptitude.py << 'EOF'
import pytest


@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={
        "username": "aptitudeuser",
        "email": "aptitude@example.com",
        "password": "pass123"
    })
    response = client.post("/api/auth/login", json={
        "username": "aptitudeuser",
        "password": "pass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_question(client, auth_headers):
    response = client.post("/api/aptitude/questions", json={
        "question_type": "判断推理",
        "question_text": "以下哪项最能加强论点？",
        "options": {"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"},
        "correct_answer": "C",
        "difficulty": 3
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["question_type"] == "判断推理"
    assert data["correct_answer"] == "C"
    assert "id" in data


def test_list_questions(client, auth_headers):
    client.post("/api/aptitude/questions", json={
        "question_type": "言语理解",
        "question_text": "填入最恰当的词语",
        "correct_answer": "A"
    }, headers=auth_headers)
    response = client.get("/api/aptitude/questions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_create_attempt(client, auth_headers):
    q_resp = client.post("/api/aptitude/questions", json={
        "question_type": "资料分析",
        "question_text": "根据图表计算增长率",
        "correct_answer": "B"
    }, headers=auth_headers)
    q_id = q_resp.json()["id"]

    response = client.post("/api/aptitude/attempts", json={
        "question_id": q_id,
        "user_answer": "B",
        "time_spent_seconds": 120
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] == True
    assert data["is_mistake"] == False


def test_create_attempt_wrong_answer(client, auth_headers):
    q_resp = client.post("/api/aptitude/questions", json={
        "question_type": "数量关系",
        "question_text": "计算工程问题",
        "correct_answer": "D"
    }, headers=auth_headers)
    q_id = q_resp.json()["id"]

    response = client.post("/api/aptitude/attempts", json={
        "question_id": q_id,
        "user_answer": "A",
        "time_spent_seconds": 180
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] == False
    assert data["is_mistake"] == True
EOF
```

- [ ] **Step 3: 运行测试**

```bash
cd /home/yufeng/gongkao-brain/backend
pytest tests/test_aptitude.py -v
```

Expected output: 4 tests passed.

- [ ] **Step 4: Commit**

```bash
git add backend/app/routers/aptitude.py backend/tests/test_aptitude.py
git commit -m "feat: add aptitude question and attempt CRUD APIs

- Add POST/GET/PUT/DELETE for questions
- Add attempt creation with auto correct/mistake detection
- Add filtering by question_type and pagination
- Add comprehensive tests

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: AI 聊天 API (SSE 流式)

**Files:**
- Create: `backend/app/services/ai_service.py`
- Create: `backend/app/routers/chat.py`
- Create: `backend/tests/test_chat.py`

- [ ] **Step 1: 创建 AI 服务**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/services/ai_service.py << 'EOF'
import httpx
import json
from typing import AsyncGenerator, List, Dict, Any
from app.config import settings

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"


async def stream_claude_response(
    messages: List[Dict[str, str]],
    context: Dict[str, Any] = None
) -> AsyncGenerator[str, None]:
    system_message = "你是一个公务员考试备考助手，擅长行测和申论辅导。"
    if context:
        context_str = json.dumps(context, ensure_ascii=False)
        system_message += f"\n\n当前页面上下文: {context_str}"

    headers = {
        "x-api-key": settings.claude_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": settings.claude_model,
        "max_tokens": 4096,
        "system": system_message,
        "messages": messages,
        "stream": True,
    }

    async with httpx.AsyncClient() as client:
        async with client.stream("POST", CLAUDE_API_URL, headers=headers, json=payload, timeout=120) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        yield json.dumps({"delta": "", "done": True})
                        break
                    try:
                        event = json.loads(data)
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {})
                            if "text" in delta:
                                yield json.dumps({"delta": delta["text"], "done": False})
                    except json.JSONDecodeError:
                        continue
EOF
```

- [ ] **Step 2: 创建聊天路由**

```bash
cat > /home/yufeng/gongkao-brain/backend/app/routers/chat.py << 'EOF'
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
EOF
```

- [ ] **Step 3: 创建聊天测试（mock 版本）**

```bash
cat > /home/yufeng/gongkao-brain/backend/tests/test_chat.py << 'EOF'
import pytest
from unittest.mock import patch, AsyncMock


@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={
        "username": "chatuser",
        "email": "chat@example.com",
        "password": "pass123"
    })
    response = client.post("/api/auth/login", json={
        "username": "chatuser",
        "password": "pass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_chat_stream(client, auth_headers):
    mock_chunks = [
        '{"delta": "Hello", "done": false}',
        '{"delta": " world", "done": false}',
        '{"delta": "", "done": true}'
    ]

    async def mock_generator(*args, **kwargs):
        for chunk in mock_chunks:
            yield chunk

    with patch("app.routers.chat.stream_claude_response", side_effect=mock_generator):
        response = client.post("/api/chat/stream", json={
            "messages": [{"role": "user", "content": "Hi"}],
            "context": {"page": "dashboard"}
        }, headers=auth_headers)

        assert response.status_code == 200
        content = response.text
        assert "data:" in content
        assert "Hello" in content
EOF
```

- [ ] **Step 4: 运行测试**

```bash
cd /home/yufeng/gongkao-brain/backend
pytest tests/test_chat.py -v
```

Expected output: 1 test passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/ai_service.py backend/app/routers/chat.py backend/tests/test_chat.py
git commit -m "feat: add AI chat API with SSE streaming

- Add Claude API integration with streaming response
- Add /api/chat/stream endpoint with context injection
- Add auth protection for chat endpoint
- Add mocked chat tests

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 7: 前端基础架构

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.ts`

- [ ] **Step 1: 创建 package.json**

```bash
mkdir -p /home/yufeng/gongkao-brain/frontend/src/{views,components,stores,api,router}

cat > /home/yufeng/gongkao-brain/frontend/package.json << 'EOF'
{
  "name": "gongkao-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "element-plus": "^2.8.0",
    "@element-plus/icons-vue": "^2.3.0",
    "axios": "^1.7.0",
    "echarts": "^5.5.0",
    "vue-echarts": "^7.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0",
    "vue-tsc": "^2.1.0",
    "@types/node": "^22.0.0"
  }
}
EOF
```

- [ ] **Step 2: 创建 Vite 配置**

```bash
cat > /home/yufeng/gongkao-brain/frontend/vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
EOF
```

- [ ] **Step 3: 创建 TypeScript 配置**

```bash
cat > /home/yufeng/gongkao-brain/frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"]
}
EOF
```

- [ ] **Step 4: 创建 index.html**

```bash
cat > /home/yufeng/gongkao-brain/frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>公考大脑</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
EOF
```

- [ ] **Step 5: 创建 main.ts**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/main.ts << 'EOF'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
EOF
```

- [ ] **Step 6: 创建路由**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/router/index.ts << 'EOF'
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import AptitudeQuestionList from '../views/AptitudeQuestionList.vue'
import AptitudeQuestionForm from '../views/AptitudeQuestionForm.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    { path: '/', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/aptitude/questions', component: AptitudeQuestionList, meta: { requiresAuth: true } },
    { path: '/aptitude/questions/new', component: AptitudeQuestionForm, meta: { requiresAuth: true } },
    { path: '/aptitude/questions/:id/edit', component: AptitudeQuestionForm, meta: { requiresAuth: true } },
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
EOF
```

- [ ] **Step 7: 创建 App.vue**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/App.vue << 'EOF'
<template>
  <div id="app">
    <NavigationMenu v-if="isLoggedIn" />
    <router-view />
    <ChatPanel v-if="isLoggedIn" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import NavigationMenu from './components/NavigationMenu.vue'
import ChatPanel from './views/ChatPanel.vue'

const isLoggedIn = computed(() => !!localStorage.getItem('token'))
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
#app { min-height: 100vh; background: #f5f7fa; }
</style>
EOF
```

- [ ] **Step 8: 安装前端依赖**

```bash
cd /home/yufeng/gongkao-brain/frontend
npm install
```

Expected output: packages installed successfully.

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat: add Vue3 frontend foundation

- Add Vue3 + Vite + TypeScript + Element Plus
- Add Pinia state management
- Add Vue Router with auth guards
- Add proxy config for API

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 8: 前端认证页面

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/stores/auth.ts`
- Create: `frontend/src/views/LoginView.vue`
- Create: `frontend/src/views/RegisterView.vue`

- [ ] **Step 1: 创建 API 客户端**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/api/client.ts << 'EOF'
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default client
EOF
```

- [ ] **Step 2: 创建认证 API**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/api/auth.ts << 'EOF'
import client from './client'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export const authApi = {
  login: (data: LoginData) => client.post('/auth/login', data),
  register: (data: RegisterData) => client.post('/auth/register', data),
}
EOF
```

- [ ] **Step 3: 创建认证 Store**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/stores/auth.ts << 'EOF'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref('')

  const login = async (username: string, password: string) => {
    const res = await authApi.login({ username, password })
    token.value = res.data.access_token
    localStorage.setItem('token', token.value)
    return res.data
  }

  const register = async (username: string, email: string, password: string) => {
    const res = await authApi.register({ username, email, password })
    return res.data
  }

  const logout = () => {
    token.value = ''
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  return { token, username, login, register, logout }
})
EOF
```

- [ ] **Step 4: 创建登录页面**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/views/LoginView.vue << 'EOF'
<template>
  <div class="login-container">
    <el-card class="login-card" style="width: 400px">
      <h2 style="text-align: center; margin-bottom: 24px">公考大脑</h2>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" style="width: 100%">登录</el-button>
        </el-form-item>
        <div style="text-align: center">
          <el-link @click="$router.push('/register')">没有账号？立即注册</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({ username: '', password: '' })

const handleLogin = async () => {
  try {
    await authStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '登录失败')
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
EOF
```

- [ ] **Step 5: 创建注册页面**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/views/RegisterView.vue << 'EOF'
<template>
  <div class="register-container">
    <el-card class="register-card" style="width: 400px">
      <h2 style="text-align: center; margin-bottom: 24px">注册账号</h2>
      <el-form :model="form" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱" prefix-icon="Message" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRegister" style="width: 100%">注册</el-button>
        </el-form-item>
        <div style="text-align: center">
          <el-link @click="$router.push('/login')">已有账号？去登录</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({ username: '', email: '', password: '' })

const handleRegister = async () => {
  try {
    await authStore.register(form.username, form.email, form.password)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '注册失败')
  }
}
</script>

<style scoped>
.register-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
EOF
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api/ frontend/src/stores/ frontend/src/views/LoginView.vue frontend/src/views/RegisterView.vue
git commit -m "feat: add frontend auth pages and API client

- Add axios client with JWT interceptors
- Add Pinia auth store
- Add LoginView and RegisterView with Element Plus
- Add auto redirect on 401

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 9: 前端导航与仪表盘

**Files:**
- Create: `frontend/src/components/NavigationMenu.vue`
- Create: `frontend/src/views/DashboardView.vue`

- [ ] **Step 1: 创建导航菜单**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/components/NavigationMenu.vue << 'EOF'
<template>
  <el-menu
    :default-active="$route.path"
    class="nav-menu"
    router
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409EFF"
  >
    <div class="logo">
      <span>公考大脑</span>
    </div>
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <span>仪表盘</span>
    </el-menu-item>
    <el-menu-item index="/aptitude/questions">
      <el-icon><Document /></el-icon>
      <span>行测错题</span>
    </el-menu-item>
    <div class="logout">
      <el-button type="danger" size="small" @click="logout">
        <el-icon><SwitchButton /></el-icon> 退出
      </el-button>
    </div>
  </el-menu>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import { HomeFilled, Document, SwitchButton } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const logout = () => authStore.logout()
</script>

<style scoped>
.nav-menu {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 200px;
  z-index: 100;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #1f2d3d;
}
.logout {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
}
</style>
EOF
```

- [ ] **Step 2: 创建仪表盘页面**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/views/DashboardView.vue << 'EOF'
<template>
  <div class="dashboard">
    <h1>学习仪表盘</h1>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <div class="stat-title">今日做题</div>
          <div class="stat-value">{{ stats.todayQuestions }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-title">正确率</div>
          <div class="stat-value">{{ stats.todayAccuracy }}%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-title">错题总数</div>
          <div class="stat-value">{{ stats.totalMistakes }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-title">学习天数</div>
          <div class="stat-value">{{ stats.studyDays }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top: 20px">
      <template #header>
        <span>快捷入口</span>
      </template>
      <el-button type="primary" @click="$router.push('/aptitude/questions/new')">
        <el-icon><Plus /></el-icon> 录入错题
      </el-button>
      <el-button @click="$router.push('/aptitude/questions')">
        <el-icon><List /></el-icon> 查看错题
      </el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { Plus, List } from '@element-plus/icons-vue'

const stats = reactive({
  todayQuestions: 0,
  todayAccuracy: 0,
  totalMistakes: 0,
  studyDays: 0
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  margin-left: 200px;
}
.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}
</style>
EOF
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/NavigationMenu.vue frontend/src/views/DashboardView.vue
git commit -m "feat: add navigation menu and dashboard

- Add fixed sidebar navigation with Element Plus menu
- Add dashboard with stat cards and quick actions
- Adjust main content margin for sidebar

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 10: 前端行测错题管理

**Files:**
- Create: `frontend/src/api/aptitude.ts`
- Create: `frontend/src/stores/aptitude.ts`
- Create: `frontend/src/views/AptitudeQuestionList.vue`
- Create: `frontend/src/views/AptitudeQuestionForm.vue`

- [ ] **Step 1: 创建行测 API**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/api/aptitude.ts << 'EOF'
import client from './client'

export interface Question {
  id: string
  question_type: string
  question_text: string
  question_image_url?: string
  options?: Record<string, string>
  correct_answer?: string
  difficulty: number
  created_at: string
}

export interface QuestionList {
  items: Question[]
  total: number
}

export interface Attempt {
  id: string
  question_id: string
  user_answer: string
  is_correct: boolean
  is_mistake: boolean
  attempt_date: string
}

export const aptitudeApi = {
  createQuestion: (data: Partial<Question>) => client.post('/aptitude/questions', data),
  listQuestions: (params?: { question_type?: string; skip?: number; limit?: number }) =>
    client.get('/aptitude/questions', { params }),
  getQuestion: (id: string) => client.get(`/aptitude/questions/${id}`),
  updateQuestion: (id: string, data: Partial<Question>) => client.put(`/aptitude/questions/${id}`, data),
  deleteQuestion: (id: string) => client.delete(`/aptitude/questions/${id}`),
  createAttempt: (data: { question_id: string; user_answer: string; time_spent_seconds?: number }) =>
    client.post('/aptitude/attempts', data),
}
EOF
```

- [ ] **Step 2: 创建行测 Store**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/stores/aptitude.ts << 'EOF'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { aptitudeApi, type Question, type QuestionList } from '../api/aptitude'

export const useAptitudeStore = defineStore('aptitude', () => {
  const questions = ref<Question[]>([])
  const total = ref(0)

  const fetchQuestions = async (params?: { question_type?: string }) => {
    const res = await aptitudeApi.listQuestions(params)
    questions.value = res.data.items
    total.value = res.data.total
  }

  const createQuestion = async (data: Partial<Question>) => {
    const res = await aptitudeApi.createQuestion(data)
    return res.data
  }

  const deleteQuestion = async (id: string) => {
    await aptitudeApi.deleteQuestion(id)
    questions.value = questions.value.filter(q => q.id !== id)
  }

  const submitAttempt = async (data: { question_id: string; user_answer: string }) => {
    const res = await aptitudeApi.createAttempt(data)
    return res.data
  }

  return { questions, total, fetchQuestions, createQuestion, deleteQuestion, submitAttempt }
})
EOF
```

- [ ] **Step 3: 创建错题列表页**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/views/AptitudeQuestionList.vue << 'EOF'
<template>
  <div class="question-list">
    <h1>行测错题</h1>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>错题列表</span>
          <el-button type="primary" @click="$router.push('/aptitude/questions/new')">
            <el-icon><Plus /></el-icon> 新增错题
          </el-button>
        </div>
      </template>
      <el-table :data="aptitudeStore.questions" style="width: 100%">
        <el-table-column prop="question_type" label="题型" width="120" />
        <el-table-column prop="question_text" label="题目" show-overflow-tooltip />
        <el-table-column prop="correct_answer" label="答案" width="80" />
        <el-table-column prop="difficulty" label="难度" width="80">
          <template #default="{ row }">
            <el-rate :model-value="row.difficulty" disabled :max="5" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="openAttemptDialog(row)">作答</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="attemptDialogVisible" title="作答" width="500px">
      <div v-if="selectedQuestion" style="margin-bottom: 16px">
        <p><strong>题目：</strong>{{ selectedQuestion.question_text }}</p>
        <div v-if="selectedQuestion.options" style="margin-top: 8px">
          <p v-for="(text, key) in selectedQuestion.options" :key="key">
            <strong>{{ key }}.</strong> {{ text }}
          </p>
        </div>
      </div>
      <el-form>
        <el-form-item label="你的答案">
          <el-input v-model="attemptForm.user_answer" placeholder="输入答案（如 A/B/C/D）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="attemptDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAttempt">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAptitudeStore } from '../stores/aptitude'
import type { Question } from '../api/aptitude'

const aptitudeStore = useAptitudeStore()
const attemptDialogVisible = ref(false)
const selectedQuestion = ref<Question | null>(null)
const attemptForm = ref({ user_answer: '' })

onMounted(() => {
  aptitudeStore.fetchQuestions()
})

const openAttemptDialog = (question: Question) => {
  selectedQuestion.value = question
  attemptForm.value.user_answer = ''
  attemptDialogVisible.value = true
}

const submitAttempt = async () => {
  if (!selectedQuestion.value) return
  try {
    const result = await aptitudeStore.submitAttempt({
      question_id: selectedQuestion.value.id,
      user_answer: attemptForm.value.user_answer
    })
    if (result.is_correct) {
      ElMessage.success('回答正确！')
    } else {
      ElMessage.warning(`回答错误，正确答案是 ${selectedQuestion.value.correct_answer}`)
    }
    attemptDialogVisible.value = false
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '提交失败')
  }
}

const handleDelete = async (id: string) => {
  try {
    await ElMessageBox.confirm('确定删除这道题目吗？', '提示', { type: 'warning' })
    await aptitudeStore.deleteQuestion(id)
    ElMessage.success('删除成功')
  } catch {
    // cancelled
  }
}
</script>

<style scoped>
.question-list {
  padding: 20px;
  margin-left: 200px;
}
</style>
EOF
```

- [ ] **Step 4: 创建错题表单页**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/views/AptitudeQuestionForm.vue << 'EOF'
<template>
  <div class="question-form">
    <h1>{{ isEdit ? '编辑错题' : '新增错题' }}</h1>
    <el-card style="max-width: 800px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="题型">
          <el-select v-model="form.question_type" placeholder="选择题型">
            <el-option label="政治理论" value="政治理论" />
            <el-option label="常识判断" value="常识判断" />
            <el-option label="言语理解" value="言语理解" />
            <el-option label="数量关系" value="数量关系" />
            <el-option label="判断推理" value="判断推理" />
            <el-option label="资料分析" value="资料分析" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目内容">
          <el-input v-model="form.question_text" type="textarea" :rows="4" placeholder="输入题目内容" />
        </el-form-item>
        <el-form-item label="选项 A">
          <el-input v-model="form.options.A" placeholder="选项 A" />
        </el-form-item>
        <el-form-item label="选项 B">
          <el-input v-model="form.options.B" placeholder="选项 B" />
        </el-form-item>
        <el-form-item label="选项 C">
          <el-input v-model="form.options.C" placeholder="选项 C" />
        </el-form-item>
        <el-form-item label="选项 D">
          <el-input v-model="form.options.D" placeholder="选项 D" />
        </el-form-item>
        <el-form-item label="正确答案">
          <el-radio-group v-model="form.correct_answer">
            <el-radio-button label="A" />
            <el-radio-button label="B" />
            <el-radio-button label="C" />
            <el-radio-button label="D" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="难度">
          <el-rate v-model="form.difficulty" :max="5" show-score />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">保存</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAptitudeStore } from '../stores/aptitude'

const router = useRouter()
const route = useRoute()
const aptitudeStore = useAptitudeStore()
const isEdit = computed(() => !!route.params.id)

const form = reactive({
  question_type: '判断推理',
  question_text: '',
  options: { A: '', B: '', C: '', D: '' },
  correct_answer: '',
  difficulty: 3
})

const handleSubmit = async () => {
  try {
    await aptitudeStore.createQuestion({ ...form })
    ElMessage.success('保存成功')
    router.push('/aptitude/questions')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '保存失败')
  }
}
</script>

<style scoped>
.question-form {
  padding: 20px;
  margin-left: 200px;
}
</style>
EOF
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/aptitude.ts frontend/src/stores/aptitude.ts frontend/src/views/AptitudeQuestionList.vue frontend/src/views/AptitudeQuestionForm.vue
git commit -m "feat: add frontend aptitude question management

- Add question list with attempt dialog
- Add question create/edit form
- Add question type selector with 6 modules
- Add answer submission with correct/mistake feedback

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 11: 前端 AI 聊天面板

**Files:**
- Create: `frontend/src/api/chat.ts`
- Create: `frontend/src/stores/chat.ts`
- Create: `frontend/src/views/ChatPanel.vue`
- Create: `frontend/src/components/ChatMessage.vue`

- [ ] **Step 1: 创建聊天 API**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/api/chat.ts << 'EOF'
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export const chatApi = {
  streamChat: (messages: ChatMessage[], context?: Record<string, unknown>) => {
    return fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      },
      body: JSON.stringify({ messages, context })
    })
  }
}
EOF
```

- [ ] **Step 2: 创建聊天 Store**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/stores/chat.ts << 'EOF'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatApi, type ChatMessage } from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([
    { role: 'assistant', content: '你好！我是你的公考备考助手，有什么可以帮你的吗？' }
  ])
  const isLoading = ref(false)

  const sendMessage = async (content: string, context?: Record<string, unknown>) => {
    const userMessage: ChatMessage = { role: 'user', content }
    messages.value.push(userMessage)
    isLoading.value = true

    const assistantMessage: ChatMessage = { role: 'assistant', content: '' }
    messages.value.push(assistantMessage)

    try {
      const response = await chatApi.streamChat(messages.value.slice(0, -1), context)
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        assistantMessage.content = '抱歉，连接出现问题。'
        isLoading.value = false
        return
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data.trim() === '[DONE]') continue
            try {
              const parsed = JSON.parse(data)
              if (parsed.delta) {
                assistantMessage.content += parsed.delta
              }
              if (parsed.done) {
                isLoading.value = false
              }
            } catch {
              // ignore parse errors
            }
          }
        }
      }
    } catch {
      assistantMessage.content = '抱歉，请求失败，请稍后重试。'
    } finally {
      isLoading.value = false
    }
  }

  const clearMessages = () => {
    messages.value = [{ role: 'assistant', content: '你好！我是你的公考备考助手，有什么可以帮你的吗？' }]
  }

  return { messages, isLoading, sendMessage, clearMessages }
})
EOF
```

- [ ] **Step 3: 创建聊天面板**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/views/ChatPanel.vue << 'EOF'
<template>
  <div class="chat-panel">
    <div v-if="!isOpen" class="chat-button" @click="isOpen = true">
      <el-icon size="24"><ChatDotRound /></el-icon>
    </div>
    <div v-else class="chat-window">
      <div class="chat-header">
        <span>AI 助手</span>
        <div>
          <el-button text size="small" @click="chatStore.clearMessages">清空</el-button>
          <el-button text size="small" @click="isOpen = false">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="chat-messages" ref="messagesRef">
        <ChatMessage
          v-for="(msg, index) in chatStore.messages"
          :key="index"
          :message="msg"
        />
        <div v-if="chatStore.isLoading" class="loading">
          <el-icon class="is-loading"><Loading /></el-icon> 思考中...
        </div>
      </div>
      <div class="chat-input">
        <el-input
          v-model="inputText"
          placeholder="输入问题..."
          @keyup.enter="sendMessage"
        >
          <template #append>
            <el-button @click="sendMessage" :loading="chatStore.isLoading">发送</el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { ChatDotRound, Close, Loading } from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat'
import ChatMessage from '../components/ChatMessage.vue'

const chatStore = useChatStore()
const isOpen = ref(false)
const inputText = ref('')
const messagesRef = ref<HTMLElement>()

watch(() => chatStore.messages.length, () => {
  nextTick(() => {
    messagesRef.value?.scrollTo(0, messagesRef.value.scrollHeight)
  })
})

const sendMessage = () => {
  if (!inputText.value.trim() || chatStore.isLoading) return
  chatStore.sendMessage(inputText.value)
  inputText.value = ''
}
</script>

<style scoped>
.chat-panel {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 1000;
}
.chat-button {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  transition: transform 0.2s;
}
.chat-button:hover {
  transform: scale(1.1);
}
.chat-window {
  width: 400px;
  height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.chat-header {
  padding: 12px 16px;
  background: #409EFF;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
}
.chat-input {
  padding: 12px;
  border-top: 1px solid #e4e7ed;
}
.loading {
  text-align: center;
  color: #909399;
  padding: 8px;
}
</style>
EOF
```

- [ ] **Step 4: 创建聊天消息组件**

```bash
cat > /home/yufeng/gongkao-brain/frontend/src/components/ChatMessage.vue << 'EOF'
<template>
  <div :class="['message', message.role]">
    <div class="avatar">
      <el-avatar :size="32" :icon="message.role === 'user' ? UserFilled : Service" />
    </div>
    <div class="bubble">
      <div class="content" v-html="formattedContent"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { UserFilled, Service } from '@element-plus/icons-vue'
import type { ChatMessage } from '../api/chat'

const props = defineProps<{ message: ChatMessage }>()

const formattedContent = computed(() => {
  return props.message.content
    .replace(/\n/g, '<br>')
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
})
</script>

<style scoped>
.message {
  display: flex;
  margin-bottom: 16px;
  gap: 12px;
}
.message.user {
  flex-direction: row-reverse;
}
.message.user .bubble {
  background: #409EFF;
  color: white;
}
.bubble {
  max-width: 280px;
  padding: 10px 14px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  word-break: break-word;
}
.content pre {
  background: #282c34;
  color: #abb2bf;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}
</style>
EOF
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/chat.ts frontend/src/stores/chat.ts frontend/src/views/ChatPanel.vue frontend/src/components/ChatMessage.vue
git commit -m "feat: add AI chat panel with SSE streaming

- Add floating chat button and expandable panel
- Add SSE streaming message display
- Add markdown-like formatting for code blocks
- Add auto-scroll to latest message

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 12: 集成测试与部署验证

**Files:**
- Modify: `docker-compose.yml`

- [ ] **Step 1: 更新 docker-compose 添加后端服务**

```bash
cat > /home/yufeng/gongkao-brain/docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: ankane/pgvector:latest
    container_name: gongkao-db
    environment:
      POSTGRES_USER: gongkao
      POSTGRES_PASSWORD: gongkao_pass
      POSTGRES_DB: gongkao
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U gongkao"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: gongkao-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio:latest
    container_name: gongkao-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  backend:
    build: ./backend
    container_name: gongkao-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://gongkao:gongkao_pass@db:5432/gongkao
      - REDIS_URL=redis://redis:6379/0
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev-secret-key}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
  redis_data:
  minio_data:
EOF
```

- [ ] **Step 2: 运行所有后端测试**

```bash
cd /home/yufeng/gongkao-brain/backend
source venv/bin/activate
pytest tests/ -v
```

Expected output: All 9 tests passed.

- [ ] **Step 3: 启动完整开发环境**

```bash
cd /home/yufeng/gongkao-brain
docker-compose up -d
```

- [ ] **Step 4: 验证 API 健康检查**

```bash
curl http://localhost:8000/api/health
```

Expected output: `{"status":"ok"}`

- [ ] **Step 5: 验证前端构建**

```bash
cd /home/yufeng/gongkao-brain/frontend
npm run build
```

Expected output: `dist/` directory created without errors.

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml
git commit -m "chore: update docker-compose with backend service

- Add backend service with auto-reload for development
- Add dependency health checks
- Add volume mount for hot reload

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Self-Review Checklist

### 1. Spec Coverage

| Spec 需求 | 对应 Task |
|---------|----------|
| 用户注册/登录/认证系统 | Task 4 |
| 行测错题录入（文本） | Task 5 + Task 10 |
| 行测基础知识分类和错题标记 | Task 5 + Task 10 |
| AI 聊天面板（SSE 流式对话） | Task 6 + Task 11 |
| 图片 OCR 录入 | 本期未实现，预留接口（question_image_url 字段） |
| 知识图谱可视化 | 本期未实现，预留 Graphify 输出目录 |
| 80 分目标拆解 | 本期未实现，后端预留 stats API 接口 |

### 2. Placeholder Scan

- [x] 无 "TBD"、"TODO"、"implement later"
- [x] 所有代码步骤包含完整可运行代码
- [x] 所有测试包含完整断言
- [x] 所有命令包含预期输出

### 3. Type Consistency

- [x] `UserResponse` 模型在 auth 和 aptitude 测试中一致使用
- [x] `AptitudeQuestionResponse` 在 API 和 Store 中字段一致
- [x] `ChatMessage` 接口在前端 API 和 Store 中一致

---

## 执行后验证清单

完成所有 Task 后，系统应满足以下条件：

- [ ] `docker-compose up -d` 成功启动 postgres + redis + minio + backend
- [ ] `pytest tests/` 通过全部 9 个测试
- [ ] `curl http://localhost:8000/api/health` 返回 `{"status":"ok"}`
- [ ] 前端 `npm run dev` 可在 `http://localhost:5173` 访问
- [ ] 可注册新用户并登录
- [ ] 可录入行测错题（文本）
- [ ] 可对错题进行作答，系统判定对错
- [ ] AI 聊天面板可发送消息并接收流式回复（需配置 CLAUDE_API_KEY）
