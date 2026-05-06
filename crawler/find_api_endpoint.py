"""
Capture POST/API calls from DVC detail page to find the REST API endpoint.
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        api_calls = []

        async def handle_request(request):
            if request.method == "POST" or "rest" in request.url or "api" in request.url.lower() or "csdl" in request.url:
                entry = {"method": request.method, "url": request.url}
                try:
                    entry["post_data"] = request.post_data
                except:
                    pass
                api_calls.append(entry)

        all_responses = []

        async def handle_response(response):
            url = response.url
            method = response.request.method
            try:
                body = await response.body()
                text = body.decode("utf-8", errors="replace")
            except:
                text = ""
            entry = {"method": method, "url": url, "body_preview": text[:200]}
            all_responses.append(entry)
            if "ma_thu_tuc" in text or "ten_thu_tuc" in text or "ten_tthc" in text:
                print(f"\n=== FOUND DATA from [{method}] {url} ===")
                print(text[:800])
            elif method == "POST":
                print(f"POST response: {url} → {text[:100]}")

        page.on("request", handle_request)
        page.on("response", handle_response)

        url = "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001640"
        print(f"Loading: {url}")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(5)

        print("\n=== All POST/API requests ===")
        for r in api_calls:
            print(r)

        print("\n=== POST responses ===")
        for r in all_responses:
            if r["method"] == "POST":
                print(r)

        await browser.close()

asyncio.run(main())
