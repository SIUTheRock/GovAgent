"""
Dùng Playwright crawl link tải mẫu đơn trực tiếp từ dichvucong.gov.vn.
- Mỗi thủ tục dùng page mới (tránh JS giữ state cũ).
- Lọc bỏ link có ma= rỗng, trùng lặp.
- Cập nhật DB và procedures_raw.json.
"""
import asyncio
import json
import os
import re
import psycopg2
from playwright.async_api import async_playwright

DB_CONFIG = {
    "host": "localhost",
    "port": 4321,
    "database": "hanhchinh_db",
    "user": "postgres",
    "password": "123",
}

RAW_JSON = os.path.join(os.path.dirname(__file__), "data", "procedures_raw.json")
DVC_URL  = "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc={code}"
CSDL_BASE = "https://csdl.dichvucong.gov.vn"

# Mã A/B không tồn tại trên DVC — map về mã cha
FAKE_CODE_MAP = {
    "1.004850A": "1.004850",
    "2.001682A": "2.001682",
    "2.000850A": "2.000850",
    "2.000850B": "2.000850",
}


async def get_forms(browser, code: str) -> list[dict]:
    real_code = FAKE_CODE_MAP.get(code, code)
    url = DVC_URL.format(code=real_code)

    # Tạo page mới cho mỗi thủ tục để tránh JS giữ state
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=35000)
    except Exception:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        except Exception as e:
            print(f"    [SKIP] goto failed: {e}")
            await page.close()
            return []

    # Đợi thêm để JS render xong bảng mẫu đơn
    await page.wait_for_timeout(3000)

    html = await page.content()
    await page.close()

    # Pattern: href="...download_file.jsp?ma=<hash>">Tên file</a>
    pattern = re.compile(
        r'href="([^"]*download_file\.jsp\?ma=([0-9a-f]{16,}))"[^>]*>\s*([^<]+?)\s*<',
        re.IGNORECASE,
    )
    forms = []
    seen = set()
    for m in pattern.finditer(html):
        href, ma_hash, name = m.group(1), m.group(2), m.group(3).strip()
        if not ma_hash or ma_hash in seen:
            continue
        seen.add(ma_hash)
        if not href.startswith("http"):
            href = CSDL_BASE + href
        name = re.sub(r'\s+', ' ', name)
        forms.append({"name": name, "url": href})

    return forms


async def main():
    with open(RAW_JSON, encoding="utf-8") as f:
        procedures = json.load(f)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, code FROM procedures")
    db_map = {row[1]: row[0] for row in cur.fetchall()}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        total = len(procedures)
        found_count = 0

        for i, proc in enumerate(procedures, 1):
            code = proc.get("code", "")
            name = proc.get("name", "")[:50]
            print(f"[{i}/{total}] {code} — {name}")

            forms = await get_forms(browser, code)

            if forms:
                found_count += 1
                print(f"  → {len(forms)} mẫu đơn:")
                for f in forms:
                    print(f"     • {f['name']} | {f['url']}")
                proc["form_templates"] = forms
            else:
                print(f"  → Không tìm thấy — giữ link trang DVC")
                real_code = FAKE_CODE_MAP.get(code, code)
                proc["form_templates"] = [{
                    "name": "Xem mẫu đơn và tải về trên Cổng Dịch vụ công Quốc gia",
                    "code": "dichvucong.gov.vn",
                    "url": DVC_URL.format(code=real_code),
                }]

            # Cập nhật DB
            proc_id = db_map.get(code)
            if proc_id:
                cur.execute(
                    "UPDATE procedures SET form_templates = %s WHERE code = %s",
                    (json.dumps(proc["form_templates"], ensure_ascii=False), code),
                )
                conn.commit()

        await browser.close()

    with open(RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(procedures, f, ensure_ascii=False, indent=2)

    cur.close()
    conn.close()
    print(f"\n✅ Hoàn tất! {found_count}/{total} thủ tục có link tải trực tiếp.")


if __name__ == "__main__":
    asyncio.run(main())
