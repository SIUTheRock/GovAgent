from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    groq_api_key: str = ""
    openai_api_key: str = ""
    database_url: str = "postgresql://postgres:postgres@localhost:5432/hanhchinh_db"
    chroma_db_path: str = "./data/chroma_db"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    llm_provider: str = "groq"  # "groq", "gemini", hoặc "openai"

    class Config:
        env_file = ".env"


settings = Settings()
