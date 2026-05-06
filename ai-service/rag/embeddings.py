import os
from langchain_huggingface import HuggingFaceEmbeddings
from config import settings

_embedding_model = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Trả về embedding model (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        print(f"[Embeddings] Đang tải model: {settings.embedding_model}")
        _embedding_model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        print("[Embeddings] Model đã sẵn sàng.")
    return _embedding_model
