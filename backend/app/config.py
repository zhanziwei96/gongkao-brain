from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://gongkao:gongkao_pass@localhost:5432/gongkao"
    redis_url: str = "redis://localhost:6379/0"
    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
