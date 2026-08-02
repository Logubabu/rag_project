from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Base dirs
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    VECTOR_DB_DIR: str = os.path.join(BASE_DIR, "vector_db")
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")

    # App Config
    LLM_PROVIDER: str = "groq"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 5

    # API Keys
    GROQ_API_KEY: str = ""
    HF_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
