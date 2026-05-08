"""
Script 1: Dùng Playwright để:
1. Mở trang DVC của một thủ tục
2. Chụp TẤT CẢ network requests
3. In ra để tìm API endpoint lấy mẫu đơn

Chạy: python discover_dvc_api.py
"""
import asyncio
from playwright.async_api import async_playwright

TEST_CODE = "1.001640"  # Đăng ký khai sinh

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124",
        )
        page = await context.new_page()

        requests_log = []

        def on_request(request):
            url = request.url
            # Bỏ qua JS, CSS, fonts, images
            if any(ext in url for ext in ['.js', '.css', '.png', '.jpg', '.woff', '.ico']):
                return
            requests_log.append({
                "url": url,
                "method": request.method,
                "headers": dict(request.headers),
            })

        page.on("request", on_request)

        url = f"https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc={TEST_CODE}"
        print(f"Mở: {url}")
        await page.goto(url, wait_until="networkidle", timeout=40000)

        print(f"\n=== Tổng {len(requests_log)} requests (bỏ JS/CSS/img) ===")
        for r in requests_log:
            print(f"[{r['method']}] {r['url']}")

        # Tìm request có chứa 'api', 'json', 'tthc', 'mau-bieu', 'form', 'file'
        keywords = ['api', 'json', 'tthc', 'mau', 'form', 'file', 'download', 'ho-so', 'bieu']
        print("\n=== Requests liên quan đến API/form ===")
        for r in requests_log:
            url_lower = r['url'].lower()
            if any(kw in url_lower for kw in keywords):
                print(f"[{r['method']}] {r['url']}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
