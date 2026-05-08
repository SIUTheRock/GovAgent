"""
Crawler tự động lấy link mẫu đơn thực từ dichvucong.gov.vn
Chạy: python crawl_form_templates.py
"""
import json
import time
import re
import psycopg2
import requests
from bs4 import BeautifulSoup
from pathlib import Path

DATA_FILE = Path("data/procedures_raw.json")
DATABASE_URL = "postgresql://postgres:123@localhost:4321/hanhchinh_db"
BASE_URL = "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html"
DOWNLOAD_BASE = "https://csdl.dichvucong.gov.vn/web/jsp/download_file.jsp"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "vi-VN,vi;q=0.9",
}


def fetch_forms(code: str) -> list[dict]:
    """Fetch trang dichvucong và extract tất cả link mẫu đơn."""
    url = f"{BASE_URL}?ma_thu_tuc={code}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"  [!] HTTP {resp.status_code} for {code}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        # Tìm tất cả link có href chứa download_file.jsp
        download_links = soup.find_all("a", href=re.compile(r"download_file\.jsp\?ma="))

        forms = []
        seen_urls = set()
        for link in download_links:
            href = link.get("href", "")
            file_name = link.get_text(strip=True)
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)

            # Lấy tên giấy tờ từ ô trước (td đầu tiên của cùng hàng)
            parent_td = link.find_parent("td")
            form_label = ""
            if parent_td:
                parent_tr = parent_td.find_parent("tr")
                if parent_tr:
                    first_td = parent_tr.find("td")
                    if first_td:
                        form_label = first_td.get_text(separator=" ", strip=True)
                        # Cắt ngắn nếu quá dài
                        if len(form_label) > 120:
                            form_label = form_label[:120].rsplit(" ", 1)[0] + "..."

            # Nếu không có label thì dùng tên file
            name = form_label if form_label else file_name

            forms.append({
                "name": name,
                "code": file_name,  # tên file = mã mẫu (vd: "1.TKngkkhaisinh.doc")
                "url": href,
            })

        return forms

    except requests.RequestException as e:
        print(f"  [!] Request error for {code}: {e}")
        return []


def update_db(code: str, forms: list[dict]):
    """Cập nhật form_templates trong PostgreSQL."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        "UPDATE procedures SET form_templates = %s WHERE code = %s",
        (json.dumps(forms, ensure_ascii=False), code)
    )
    conn.commit()
    cur.close()
    conn.close()


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        procedures = json.load(f)

    total = len(procedures)
    found = 0

    for i, p in enumerate(procedures):
        code = p.get("code", "")
        name = p.get("name", "")
        print(f"[{i+1}/{total}] {code} — {name}")

        forms = fetch_forms(code)
        if forms:
            print(f"  -> Tìm được {len(forms)} mẫu đơn")
            for f in forms:
                print(f"     • {f['code']} | {f['url']}")
            found += 1
        else:
            print(f"  -> Không có mẫu đơn nào (hoặc mã không tồn tại trên DVC)")

        # Cập nhật JSON và DB
        p["form_templates"] = forms
        update_db(code, forms)

        # Tránh spam server
        time.sleep(1.5)

    # Lưu lại JSON
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(procedures, f, ensure_ascii=False, indent=2)

    print(f"\n[Done] {found}/{total} thủ tục có mẫu đơn. Đã cập nhật JSON + DB.")


if __name__ == "__main__":
    main()
