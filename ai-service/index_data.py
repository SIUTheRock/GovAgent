import psycopg2
from rag.vectorstore import add_procedures_to_vectorstore
from config import settings


def load_procedures_from_db() -> list[dict]:
    """Lấy tất cả thủ tục từ PostgreSQL."""
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.name, p.raw_content, p.level, p.implementing_agency,
               p.processing_time, c.name AS category_name
        FROM procedures p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.is_active = TRUE
    """)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


if __name__ == "__main__":
    print("[Index] Đang tải dữ liệu từ PostgreSQL...")
    procedures = load_procedures_from_db()
    print(f"[Index] Tìm thấy {len(procedures)} thủ tục.")

    if procedures:
        count = add_procedures_to_vectorstore(procedures)
        print(f"[Index] Đã nạp {count} documents vào ChromaDB.")
    else:
        print("[Index] Không có dữ liệu để nạp.")
