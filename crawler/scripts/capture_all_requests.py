"""Capture ALL network requests from DVC detail page"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        all_requests = []

        def on_request(request):
            all_requests.append({
                "method": request.method,
                "url": request.url,
                "post_data": request.post_data if request.method == "POST" else None
            })

        all_responses = []

        async def on_response(response):
            url = response.url
            method = response.request.method
            try:
                body = await response.body()
                text = body.decode("utf-8", errors="replace")
            except:
                text = ""
            all_responses.append({"method": method, "url": url, "size": len(text)})
            if method == "POST" or "csdl" in url or "rest.jsp" in url:
                print(f"[{method}] {url} ({len(text)}b)")
                if text and len(text) < 2000:
                    print("  BODY:", text[:500])

        page.on("request", on_request)
        page.on("response", on_response)

        url = "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001640"
        print(f"Loading: {url}\n")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(8)

        print(f"\n=== Total requests: {len(all_requests)} ===")
        for r in all_requests:
            print(f"  [{r['method']}] {r['url'][:100]}")
            if r['post_data']:
                print(f"    POST: {r['post_data'][:200]}")

        await browser.close()

asyncio.run(main())
