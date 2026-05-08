"""
Debug: bắt API response của trang search DVC để tìm endpoint JSON
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

QUERY = "Đăng ký khai sinh"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        json_responses = []

        async def handle_response(response):
            url = response.url
            ctype = response.headers.get("content-type", "")
            if "json" in ctype or "javascript" in ctype:
                try:
                    body = await response.body()
                    text = body.decode("utf-8", errors="replace")
                    if "ma_thu_tuc" in text or "ten_thu_tuc" in text or "tenThuTuc" in text:
                        json_responses.append({"url": url, "body": text[:2000]})
                except Exception:
                    pass

        page.on("response", handle_response)

        url = f"https://dichvucong.gov.vn/p/home/dvc-tim-kiem-thu-tuc.html?key={QUERY.replace(' ','+')}"
        print(f"Loading: {url}")
        await page.goto(url, wait_until="networkidle", timeout=35000)
        await page.wait_for_timeout(4000)

        print(f"\n=== JSON responses với mã thủ tục ({len(json_responses)}) ===")
        for r in json_responses:
            print(f"\nURL: {r['url']}")
            print(r['body'][:500])

        # Nếu không bắt được, in tất cả requests
        if not json_responses:
            print("\nKhông bắt được JSON — in tất cả network requests:")
            all_reqs = []
            page2 = await browser.new_page()
            page2.on("request", lambda r: all_reqs.append(r.url))
            await page2.goto(url, wait_until="networkidle", timeout=35000)
            await page2.wait_for_timeout(4000)
            for u in all_reqs:
                if "csdl" in u or "api" in u.lower() or "search" in u.lower() or "tim" in u.lower():
                    print(u)
            print("\n--- All requests ---")
            for u in all_reqs:
                if not any(x in u for x in ['.woff','.ttf','.png','.jpg','.ico']):
                    print(u)
            await page2.close()

        await browser.close()

asyncio.run(main())
