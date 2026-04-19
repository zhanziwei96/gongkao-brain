from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://gongkao:gongkao_pass@localhost:5432/gongkao"
    redis_url: str = "redis://localhost:6379/0"

    # LLM 配置（兼容 Claude / Kimi / OpenAI）
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""

    # 向后兼容：如果未配置 llm_xxx，则回退到 claude_xxx
    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"

    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"

    def get_llm_config(self):
        """返回实际使用的 LLM 配置"""
        api_key = self.llm_api_key or self.claude_api_key
        model = self.llm_model or self.claude_model
        # 如果没有配置 base_url，根据 api_key 前缀判断
        base_url = self.llm_base_url
        if not base_url:
            # Kimi key 以 sk- 开头且不是 sk-ant-
            if api_key.startswith("sk-") and not api_key.startswith("sk-ant-"):
                # Kimi Code 使用 Anthropic SDK 兼容格式
                base_url = "https://api.kimi.com/coding/"
            else:
                base_url = "https://api.anthropic.com"
        return {"api_key": api_key, "base_url": base_url, "model": model}


settings = Settings()
