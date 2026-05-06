import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from rag.embeddings import get_embedding_model
from config import settings


def get_vectorstore() -> Chroma:
    """Trả về ChromaDB vectorstore (singleton)."""
    os.makedirs(settings.chroma_db_path, exist_ok=True)
    embeddings = get_embedding_model()
    vectorstore = Chroma(
        collection_name="procedures",
        embedding_function=embeddings,
        persist_directory=settings.chroma_db_path,
    )
    return vectorstore


def add_procedures_to_vectorstore(procedures: list[dict]) -> int:
    """
    Thêm hoặc cập nhật thủ tục vào ChromaDB.
    procedures: list of dict với keys: id, name, raw_content, category_name, level
    Trả về số documents đã thêm.
    """
    vectorstore = get_vectorstore()

    documents = []
    ids = []
    for p in procedures:
        content = f"Tên thủ tục: {p.get('name', '')}\n"
        if p.get('category_name'):
            content += f"Lĩnh vực: {p['category_name']}\n"
        if p.get('level'):
            content += f"Cấp thực hiện: {p['level']}\n"
        if p.get('implementing_agency'):
            content += f"Cơ quan: {p['implementing_agency']}\n"
        if p.get('processing_time'):
            content += f"Thời gian: {p['processing_time']}\n"
        if p.get('raw_content'):
            content += f"\n{p['raw_content']}"

        doc = Document(
            page_content=content.strip(),
            metadata={
                "procedure_id": str(p["id"]),
                "name": p.get("name", ""),
                "category": p.get("category_name", ""),
                "level": p.get("level", ""),
            },
        )
        documents.append(doc)
        ids.append(f"proc_{p['id']}")

    if documents:
        vectorstore.add_documents(documents=documents, ids=ids)

    return len(documents)
