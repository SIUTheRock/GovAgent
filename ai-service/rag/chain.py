from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from rag.vectorstore import get_vectorstore
from config import settings

SYSTEM_PROMPT = """Bạn là trợ lý ảo hỗ trợ tra cứu thủ tục hành chính công tại TP. Hồ Chí Minh.
Nhiệm vụ của bạn là trả lời câu hỏi của người dân dựa trên thông tin thủ tục hành chính được cung cấp.

Nguyên tắc:
- Trả lời bằng tiếng Việt, rõ ràng, dễ hiểu, thân thiện
- Chỉ dựa vào thông tin được cung cấp trong phần "Thông tin tham khảo" bên dưới
- Nếu không có đủ thông tin, hãy thông báo và đề nghị người dùng liên hệ cơ quan chức năng
- Không bịa đặt hoặc suy đoán thông tin pháp lý
- Khi cần, gợi ý cụ thể tên thủ tục liên quan
- Có thể tham khảo lịch sử hội thoại để trả lời câu hỏi liên quan đến ngữ cảnh trước

Thông tin tham khảo:
{context}
"""


def _get_llm():
    """Khởi tạo LLM dựa trên cấu hình."""
    if settings.llm_provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=settings.groq_api_key,
            temperature=0.3,
        )
    elif settings.llm_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0.3,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=settings.openai_api_key,
            temperature=0.3,
        )


def build_rag_chain():
    """Xây dựng RAG chain có hỗ trợ conversation history."""
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )
    llm = _get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history", optional=True),
        ("human", "Câu hỏi: {question}"),
    ])

    def format_docs(docs):
        return "\n\n---\n\n".join(doc.page_content for doc in docs)

    chain = (
        {
            "context": itemgetter("question") | retriever | format_docs,
            "question": itemgetter("question"),
            "history": itemgetter("history"),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever


_rag_chain = None
_retriever = None


def get_rag_chain():
    global _rag_chain, _retriever
    if _rag_chain is None:
        _rag_chain, _retriever = build_rag_chain()
    return _rag_chain, _retriever


async def answer_question(question: str, history: list = None) -> dict:
    """
    Trả lời câu hỏi bằng RAG với hỗ trợ conversation history.
    history: list of {"role": "user"|"assistant", "content": "..."}
    Trả về: { answer, procedure_ids, sources }
    """
    chain, retriever = get_rag_chain()

    # Chuyển history sang LangChain messages (giới hạn 6 messages = 3 lượt)
    lc_history = []
    if history:
        for msg in history[-6:]:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                lc_history.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_history.append(AIMessage(content=content))

    # Lấy docs để trích xuất procedure_ids và sources
    docs = retriever.invoke(question)
    procedure_ids = []
    sources = []
    for doc in docs:
        pid = doc.metadata.get("procedure_id")
        if pid:
            try:
                procedure_ids.append(int(pid))
            except ValueError:
                pass
        name = doc.metadata.get("name", "")
        if name and name not in sources:
            sources.append(name)

    answer = await chain.ainvoke({"question": question, "history": lc_history})

    return {
        "answer": answer,
        "procedure_ids": list(dict.fromkeys(procedure_ids)),  # dedup, giữ thứ tự
        "sources": sources[:5],
    }
