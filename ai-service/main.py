import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from rag.chain import answer_question, get_rag_chain
from rag.vectorstore import add_procedures_to_vectorstore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động: warmup RAG chain
    print("[Startup] Đang khởi động RAG chain...")
    try:
        get_rag_chain()
        print("[Startup] RAG chain đã sẵn sàng.")
    except Exception as e:
        print(f"[Startup] Cảnh báo: {e}")
    yield


app = FastAPI(
    title="AI Service - Tra cứu Thủ tục Hành chính",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    question: str
    history: list[dict] = []

    @field_validator("question")
    @classmethod
    def validate_question(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Câu hỏi quá ngắn.")
        if len(v) > 500:
            raise ValueError("Câu hỏi quá dài (tối đa 500 ký tự).")
        return v


class IndexRequest(BaseModel):
    procedures: list[dict]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        result = await answer_question(req.question, req.history)
        return result
    except Exception as e:
        print(f"[Chat Error] {e}")
        raise HTTPException(status_code=500, detail="Lỗi xử lý câu hỏi.")


@app.post("/index")
async def index(req: IndexRequest):
    """Nạp/cập nhật thủ tục vào ChromaDB (dùng sau khi crawl xong)."""
    try:
        count = add_procedures_to_vectorstore(req.procedures)
        return {"indexed": count}
    except Exception as e:
        print(f"[Index Error] {e}")
        raise HTTPException(status_code=500, detail="Lỗi khi index dữ liệu.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
