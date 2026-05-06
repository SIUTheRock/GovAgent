"""
Xử lý dữ liệu từ file JSON và nhập vào PostgreSQL.
Chạy sau khi đã crawl xong: py process_data.py
"""

import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hanhchinh_db")
DATA_FILE = Path("data/procedures_raw.json")

CATEGORY_MAP = {
    "Hộ tịch": "ho-tich",
    "Cư trú": "cu-tru",
    "Đất đai - Nhà ở": "dat-dai-nha-o",
    "Doanh nghiệp": "doanh-nghiep",
    "Giáo dục": "giao-duc",
    "Y tế": "y-te",
    "Giao thông - Vận tải": "giao-thong-van-tai",
    "Xây dựng": "xay-dung",
    "Lao động - Việc làm": "lao-dong-viec-lam",
    "Tư pháp": "tu-phap",
}


def get_category_id(cursor, category_name: str) -> int | None:
    slug = CATEGORY_MAP.get(category_name)
    if not slug:
        return None
    cursor.execute("SELECT id FROM categories WHERE slug = %s", (slug,))
    row = cursor.fetchone()
    return row[0] if row else None


def import_to_db(procedures: list[dict]):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    inserted = 0
    skipped = 0

    for p in procedures:
        try:
            category_id = get_category_id(cur, p.get("category", ""))
            cur.execute("""
                INSERT INTO procedures (
                    code, name, category_id, level, implementing_agency,
                    processing_time, fee, requirements, procedure_steps,
                    required_documents, result, legal_basis, source_url, raw_content,
                    form_templates
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (code) DO UPDATE SET
                    name = EXCLUDED.name,
                    category_id = EXCLUDED.category_id,
                    level = EXCLUDED.level,
                    implementing_agency = EXCLUDED.implementing_agency,
                    processing_time = EXCLUDED.processing_time,
                    fee = EXCLUDED.fee,
                    requirements = EXCLUDED.requirements,
                    procedure_steps = EXCLUDED.procedure_steps,
                    required_documents = EXCLUDED.required_documents,
                    result = EXCLUDED.result,
                    legal_basis = EXCLUDED.legal_basis,
                    source_url = EXCLUDED.source_url,
                    raw_content = EXCLUDED.raw_content,
                    form_templates = EXCLUDED.form_templates,
                    updated_at = NOW()
            """, (
                p.get("code"),
                p.get("name"),
                category_id,
                p.get("level"),
                p.get("implementing_agency"),
                p.get("processing_time"),
                p.get("fee"),
                p.get("requirements"),
                p.get("procedure_steps"),
                p.get("required_documents"),
                p.get("result"),
                p.get("legal_basis"),
                p.get("source_url"),
                p.get("raw_content"),
                json.dumps(p.get("form_templates", []), ensure_ascii=False),
            ))
            inserted += 1
        except Exception as e:
            print(f"[Skip] {p.get('name', 'unknown')}: {e}")
            skipped += 1
            conn.rollback()
            continue

    conn.commit()
    cur.close()
    conn.close()
    print(f"[Import] Đã nhập: {inserted}, Bỏ qua: {skipped}")


if __name__ == "__main__":
    if not DATA_FILE.exists():
        print(f"[Error] Không tìm thấy file {DATA_FILE}. Hãy chạy crawler.py --mode sample trước.")
        exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        procedures = json.load(f)

    print(f"[Process] Đang nhập {len(procedures)} thủ tục vào database...")
    import_to_db(procedures)
    print("[Process] Hoàn tất.")
