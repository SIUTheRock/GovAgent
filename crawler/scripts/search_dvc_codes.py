"""
Use Playwright to search DVC for each procedure by name and extract the correct ma_thu_tuc code.
Renders the search page, waits for JS, extracts results.
"""
import asyncio
import re
import json
from playwright.async_api import async_playwright

# Our 30 procedures: {current_app_code: expected_name}
PROCEDURES = [
    ("1.001640", "Đăng ký khai sinh"),
    ("1.004734", "Đăng ký kết hôn"),
    ("1.001057", "Cấp Giấy chứng nhận quyền sử dụng đất"),
    ("1.001229", "Đăng ký thường trú"),
    ("2.000850", "Cấp Giấy phép lái xe"),
    ("1.004850", "Cấp Giấy phép xây dựng"),
    ("2.001682", "Đăng ký kinh doanh hộ cá thể"),
    ("1.001064", "Cấp bản sao trích lục hộ tịch"),
    ("1.003559", "Xác nhận tình trạng hôn nhân"),
    ("2.002400", "Cấp giấy khám sức khỏe"),
    ("1.004792", "Đăng ký khai tử"),
    ("1.003306", "Đăng ký tạm trú"),
    ("1.003311", "Tách hộ khẩu"),
    ("1.001123", "Chuyển mục đích sử dụng đất"),
    ("1.001125", "Đăng ký chuyển nhượng quyền sử dụng đất"),
    ("1.003453", "Cấp phiếu lý lịch tư pháp số 1"),
    ("1.003454", "Cấp phiếu lý lịch tư pháp số 2"),
    ("1.003670", "Đăng ký nhận nuôi con nuôi"),
    ("1.004621", "Đăng ký thay đổi cải chính hộ tịch"),
    ("1.004800", "Đăng ký lại khai sinh"),
    ("1.003820", "Cấp giấy chứng nhận an toàn thực phẩm"),
    ("1.005000", "Hưởng trợ cấp thất nghiệp"),
    ("1.004700", "Xác nhận hộ nghèo hộ cận nghèo"),
    ("1.005100", "Cấp giấy phép kinh doanh dịch vụ karaoke"),
    ("1.005200", "Đăng ký bảo hộ nhãn hiệu"),
    ("1.005300", "Cấp giấy phép lao động cho người nước ngoài"),
    ("1.004850A", "Điều chỉnh giấy phép xây dựng"),
    ("2.000850A", "Đổi giấy phép lái xe"),
    ("2.000850B", "Cấp lại giấy phép lái xe bị mất"),
    ("2.001682A", "Thay đổi nội dung đăng ký hộ kinh doanh"),
]

async def search_one(page, name):
    """Search DVC for a procedure by name, return list of (ma_thu_tuc, ten) found"""
    encoded = name.replace(' ', '+')
    url = f"https://dichvucong.gov.vn/p/home/dvc-tim-kiem-thu-tuc.html?key={encoded}"
    
    results = []
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(5)  # Wait for AJAX
        
        # Get full rendered HTML
        html = await page.content()
        
        # Save for inspection
        with open(f'E:/PPNCKH/crawler/data/search_{name[:15].replace(" ","_")}.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Look for procedure codes - various formats
        # 1.001640 style
        codes_dot = re.findall(r'ma_thu_tuc=([0-9]+\.[0-9]+)', html)
        # Numeric only
        codes_num = re.findall(r'"ma_thu_tuc"\s*[=:]\s*["\']?([0-9A-Z.]+)["\']?', html)
        # In href links
        codes_href = re.findall(r'ma_thu_tuc=([^"&\s]+)', html)
        
        all_codes = list(set(codes_dot + codes_num + codes_href))
        if all_codes:
            results = all_codes
            
        # Show context
        first_word = name.split()[0].lower()
        idx = html.lower().find(first_word)
        if idx > -1:
            context = html[max(0,idx-50):idx+200]
            context_clean = re.sub(r'<[^>]+>', ' ', context).strip()[:150]
            print(f"  Context: {context_clean}")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    return results

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        results_map = {}
        
        for app_code, name in PROCEDURES[:5]:  # Test first 5
            print(f"\n[{app_code}] Searching: {name}")
            page = await browser.new_page()
            codes = await search_one(page, name)
            await page.close()
            results_map[app_code] = {"name": name, "found_codes": codes}
            print(f"  Found codes: {codes}")
        
        await browser.close()
        
        print("\n\n=== RESULTS ===")
        for code, info in results_map.items():
            print(f"{code}: {info['name']}")
            print(f"  Found: {info['found_codes']}")

asyncio.run(main())
