from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
# 基础配置
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000

    # LLM配置 (来自 Infrastructure，更完整)
    llm_provider: str = "openai"
    openai_api_key: str = "your-openai-key-here"
    openai_model: str = "gpt-4o-mini"

    # Together AI配置 (来自 Infrastructure)
    together_api_key: str = "your-together-key-here"
    together_model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    # CORS配置 (保留 Infrastructure 的类型定义 List[str]，但建议暂时允许所有来源以方便开发)
    # 如果前端在 3000 端口，也可以用 ["http://localhost:3000"]
    cors_origins: list[str] = ["*"]
    # 故障转移配置
    enable_fallback: bool = True
    fallback_provider: str = "together"
    max_retries: int = 2
    retry_delay: int = 1  # seconds

    # CORS配置
    cors_origins: List[str] = ["http://localhost:3000"]

    # 文件处理 (来自 Infrastructure 的新功能)
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"

    # Pydantic V2 配置 (保留 HEAD 的新语法 + 前缀设置)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="RESUME_",  # 关键：保留这个，否则可能读不到 .env
        extra="ignore",
        case_sensitive=False
    )
        
    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./ai_job_coach.db"
    # For PostgreSQL: postgresql+asyncpg://user:password@localhost:5432/ai_job_coach
    database_echo: bool = False  # Set to True to log SQL queries

    

def get_settings():
    return Settings()