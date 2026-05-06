"""
Bắt tất cả network requests và tìm download links trong HTML được render bởi Angular.
"""
import asyncio
import re
from playwright.async_api import async_playwright

TEST_CODE = "1.001640"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"
        )
        page = await context.new_page()

        all_requests = []
        page.on("request", lambda r: all_requests.append(r.url))

        url = f"https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc={TEST_CODE}"
        print(f"Loading: {url}")
        await page.goto(url, wait_until="networkidle", timeout=40000)
        await page.wait_for_timeout(5000)

        print(f"\nTotal requests: {len(all_requests)}")
        print("=== ALL REQUESTS ===")
        for u in all_requests:
            print(u)

        # Tìm download links trong HTML rendered
        content = await page.content()

        dl = re.findall(r'download_file[^\"\' <]{0,100}', content)
        print("\n=== DOWNLOAD LINKS IN RENDERED HTML ===")
        for d in dl:
            print(d)

        # In một đoạn HTML xung quanh 'mau' hay 'bieu'
        snippets = re.findall(r'.{0,50}(?:mẫu|tờ khai|biểu mẫu|download).{0,100}', content, re.I)
        print("\n=== FORM-RELATED SNIPPETS (first 10) ===")
        for s in snippets[:10]:
            print(repr(s))

        await browser.close()

asyncio.run(main())
