from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #允许额外字段
    model_config = SettingsConfigDict(extra='ignore')
    #基础配置
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    #服务配置
    host: str = "0.0.0.0"
    
    port: int = 8000
    #LLM配置
    openai_api_key: str = "openai"
   # together_api_key: str = "togetherai"
    #CORS配置
    cors_origins: list[str] = ["*"]
    
    #pydantic v2的config 
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RESUME_",  # 可选：环境变量前缀，如 RESUME_DEBUG, RESUME_HOST
        extra="ignore",
    )

def get_settings():
    return Settings()