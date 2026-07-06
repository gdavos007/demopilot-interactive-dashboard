from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DemoPilot"
    
    # VAPI Settings
    VAPI_API_KEY: str = Field(..., env="VAPI_API_KEY")
    VAPI_ASSISTANT_ID: str = Field(..., env="VAPI_ASSISTANT_ID")
    
    # Anthropic Settings
    ANTHROPIC_API_KEY: str = Field(..., env="ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Storylane Settings
    STORYLANE_BASE_URL: str = "https://app.storylane.io/share"
    STORYLANE_SHARE_ID: str = Field(..., env="STORYLANE_SHARE_ID")
    
    # Vector Store Settings
    VECTOR_STORE_PATH: str = "data/vector_store"
    
    # Langsmith Settings
    LANGSMITH_TRACING: bool = Field(False, env="LANGSMITH_TRACING")
    LANGSMITH_ENDPOINT: str = Field("https://api.smith.langchain.com", env="LANGSMITH_ENDPOINT")
    LANGSMITH_API_KEY: Optional[str] = Field(None, env="LANGSMITH_API_KEY")
    LANGSMITH_PROJECT: Optional[str] = Field(None, env="LANGSMITH_PROJECT")
    LANGSMITH_DATASET_ID: Optional[str] = Field(None, env="LANGSMITH_DATASET_ID")

settings = Settings() 