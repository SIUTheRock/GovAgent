"""
Tìm mã thủ tục chính xác trên dichvucong.gov.vn bằng cách search theo tên.
Cập nhật lại field 'code' trong DB + JSON.

Cách hoạt động:
- Mở trang tìm kiếm DVC: https://dichvucong.gov.vn/p/home/dvc-tim-kiem-thu-tuc.html
- Search từng tên thủ tục
- Lấy mã từ kết quả đầu tiên phù hợp nhất
- So sánh với mã hiện tại, cập nhật nếu khác
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
SEARCH_URL = "https://dichvucong.gov.vn/p/home/dvc-tim-kiem-thu-tuc.html?key={query}"
DVC_DETAIL_NGANH = "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc={code}"
DVC_DETAIL_CHUNG = "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-dung-chung.html?ma_thu_tuc={code}"


def normalize(text: str) -> str:
    """Chuyển về chữ thường, bỏ dấu, chuẩn hóa khoảng trắng để so sánh."""
    import unicodedata
    text = unicodedata.normalize("NFC", text.lower().strip())
    # Giữ nguyên tiếng Việt (chỉ chuẩn hóa whitespace)
    return re.sub(r'\s+', ' ', text)


async def search_procedure(page, name: str, current_code: str) -> dict | None:
    """
    Tìm kiếm thủ tục theo tên trên DVC.
    Trả về {"code": ..., "url": ..., "title": ...} hoặc None nếu không tìm thấy.
    """
    # Lấy 4-5 từ đầu của tên để search
    keywords = ' '.join(name.split()[:6])
    search_url = SEARCH_URL.format(query=keywords.replace(' ', '+'))

    try:
        await page.goto(search_url, wait_until="networkidle", timeout=30000)
    except Exception:
        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"    [SKIP] search failed: {e}")
            return None

    html = await page.content()

    # Tìm tất cả link chi tiết thủ tục trong kết quả tìm kiếm
    # Hai dạng URL: nganh-doc và dung-chung
    pattern = re.compile(
        r'href="[^"]*dvc-chi-tiet-thu-tuc[^"]*ma_thu_tuc=([0-9.]+[A-Z]?)"[^>]*>\s*([^<]+?)\s*</a',
        re.IGNORECASE,
    )

    name_norm = normalize(name)
    best_match = None
    best_score = 0

    for m in pattern.finditer(html):
        result_code = m.group(1).strip()
        result_title = m.group(2).strip()
        title_norm = normalize(result_title)

        # Tính mức độ khớp (Jaccard đơn giản trên từ)
        words_name = set(name_norm.split())
        words_title = set(title_norm.split())
        if not words_name:
            continue
        intersection = words_name & words_title
        score = len(intersection) / len(words_name | words_title)

        if score > best_score:
            best_score = score
            best_match = {"code": result_code, "title": result_title, "score": score}

    if best_match and best_match["score"] >= 0.4:
        return best_match
    return None


async def main():
    with open(RAW_JSON, encoding="utf-8") as f:
        procedures = json.load(f)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    updates = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for proc in procedures:
            old_code = proc.get("code", "")
            name = proc.get("name", "")
            print(f"\n[{old_code}] {name[:55]}")

            page = await browser.new_page()
            result = await search_procedure(page, name, old_code)
            await page.close()

            if result:
                new_code = result["code"]
                score_pct = int(result["score"] * 100)
                if new_code != old_code:
                    print(f"  ✏️  {old_code} → {new_code}  ({score_pct}% match: \"{result['title'][:50]}\")")
                    updates.append((old_code, new_code, name))
                    proc["code"] = new_code
                    # Reset form_templates về DVC link với code mới
                    proc["form_templates"] = [{
                        "name": "Xem mẫu đơn và tải về trên Cổng Dịch vụ công Quốc gia",
                        "code": "dichvucong.gov.vn",
                        "url": DVC_DETAIL_NGANH.format(code=new_code),
                    }]
                else:
                    print(f"  ✅ Mã đúng ({score_pct}% match)")
            else:
                print(f"  ❓ Không tìm thấy kết quả phù hợp — giữ mã cũ")

        await browser.close()

    if updates:
        print(f"\n=== Cập nhật {len(updates)} mã vào DB ===")
        for old_code, new_code, name in updates:
            cur.execute(
                "UPDATE procedures SET code = %s, form_templates = %s WHERE code = %s",
                (
                    new_code,
                    json.dumps([{
                        "name": "Xem mẫu đơn và tải về trên Cổng Dịch vụ công Quốc gia",
                        "code": "dichvucong.gov.vn",
                        "url": DVC_DETAIL_NGANH.format(code=new_code),
                    }], ensure_ascii=False),
                    old_code,
                ),
            )
            print(f"  DB updated: {old_code} → {new_code}")
        conn.commit()
    else:
        print("\n✅ Tất cả mã đã đúng, không cần cập nhật.")

    with open(RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(procedures, f, ensure_ascii=False, indent=2)

    cur.close()
    conn.close()
    print("\n✅ Hoàn tất! Chạy crawl_direct_links.py để lấy link tải sau khi fix mã.")


if __name__ == "__main__":
    asyncio.run(main())
