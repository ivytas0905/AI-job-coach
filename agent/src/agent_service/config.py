from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #基础配置
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    #服务配置
    host: str = "0.0.0.0"
    port: int = 8000
    #LLM配置
    openai_api_key: str = "openai"
    #CORS配置
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings():
    return Settings()