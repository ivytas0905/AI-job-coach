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

    # LLM配置
    llm_provider: str = "openai"
    openai_api_key: str = "your-openai-key-here"
    openai_model: str = "gpt-4o-mini"

    # Together AI配置（备用）
    together_api_key: str = "your-together-key-here"
    together_model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    # 故障转移配置
    enable_fallback: bool = True
    fallback_provider: str = "together"
    max_retries: int = 2
    retry_delay: int = 1  # seconds

    # CORS配置
    cors_origins: List[str] = ["http://localhost:3000"]

    # 文件处理
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"

    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./ai_job_coach.db"
    # For PostgreSQL: postgresql+asyncpg://user:password@localhost:5432/ai_job_coach
    database_echo: bool = False  # Set to True to log SQL queries

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings():
    return Settings()