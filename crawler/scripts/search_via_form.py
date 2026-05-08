"""
Use Playwright to fill DVC search form, wait for AJAX results, and extract procedure codes.
"""
import asyncio
import re
from playwright.async_api import async_playwright

SEARCH_TERM = "Đăng ký khai sinh"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        captured_urls = []
        captured_bodies = {}

        async def on_response(response):
            url = response.url
            method = response.request.method
            if method == "POST":
                captured_urls.append(url)
                try:
                    body = await response.body()
                    text = body.decode("utf-8", errors="replace")
                    captured_bodies[url] = text
                    print(f"POST {url} → {len(text)}b: {text[:200]}")
                except Exception as e:
                    print(f"POST {url} → error: {e}")

        page.on("response", on_response)

        # Go to DVC homepage search
        print("Going to DVC homepage...")
        await page.goto("https://dichvucong.gov.vn/p/home/dvc-index.html", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # Look for search input
        print("Page loaded. Looking for search input...")
        
        # Try to find a search input
        inputs = await page.query_selector_all("input[type='text'], input[type='search'], input[placeholder]")
        for inp in inputs:
            placeholder = await inp.get_attribute("placeholder") or ""
            name = await inp.get_attribute("name") or ""
            id_ = await inp.get_attribute("id") or ""
            cls = await inp.get_attribute("class") or ""
            print(f"  Input: id={id_} name={name} placeholder={placeholder[:50]} class={cls[:40]}")

        await browser.close()

asyncio.run(main())
