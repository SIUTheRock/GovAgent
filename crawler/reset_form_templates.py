"""
Reset form_templates về link chính thức dichvucong.gov.vn
Chỉ dùng link đến trang thủ tục đúng (hoạt động trong trình duyệt thực).
"""
import json
import psycopg2
from pathlib import Path

DATA_FILE = Path("data/procedures_raw.json")
DATABASE_URL = "postgresql://postgres:123@localhost:4321/hanhchinh_db"
DVC_URL = "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc={code}"

# Các mã code "tự chế" không tồn tại trên dichvucong — map về mã cha
FAKE_CODE_MAP = {
    "1.004850A": "1.004850",   # Điều chỉnh GPXD → trang GPXD
    "2.001682A": "2.001682",   # Thay đổi HKD → trang đăng ký HKD
    "2.000850A": "2.000850",   # Đổi GPLX → trang cấp GPLX
    "2.000850B": "2.000850",   # Cấp lại GPLX → trang cấp GPLX
}

def build_forms(code: str, procedure_name: str) -> list[dict]:
    real_code = FAKE_CODE_MAP.get(code, code)
    return [{
        "name": f"Xem mẫu đơn và tải về trên Cổng Dịch vụ công Quốc gia",
        "code": "dichvucong.gov.vn",
        "url": DVC_URL.format(code=real_code),
    }]

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        procedures = json.load(f)

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    for p in procedures:
        code = p.get("code", "")
        name = p.get("name", "")
        forms = build_forms(code, name)
        p["form_templates"] = forms
        cur.execute(
            "UPDATE procedures SET form_templates = %s WHERE code = %s",
            (json.dumps(forms, ensure_ascii=False), code)
        )
        print(f"  {code} → {forms[0]['url']}")

    conn.commit()
    cur.close()
    conn.close()

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(procedures, f, ensure_ascii=False, indent=2)

    print(f"\n[Done] Đã cập nhật {len(procedures)} thủ tục.")

if __name__ == "__main__":
    main()
