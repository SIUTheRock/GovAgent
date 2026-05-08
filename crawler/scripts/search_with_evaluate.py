"""
Use Playwright + page.evaluate() to query the actual DOM for search results.
page.content() might not work, but page.evaluate() runs in the browser context
and can access dynamically loaded content.
"""
import asyncio
from playwright.async_api import async_playwright

WRONG_PROCEDURES = [
    ('1.001057', 'cấp giấy chứng nhận quyền sử dụng đất'),
    ('1.001125', 'đăng ký sang tên chuyển nhượng quyền sử dụng đất'),
    ('1.003453', 'cấp phiếu lý lịch tư pháp số 1'),
    ('1.004850', 'cấp giấy phép xây dựng nhà ở'),
    ('1.005100', 'cấp giấy phép kinh doanh karaoke'),
    ('1.005300', 'cấp giấy phép lao động người nước ngoài'),
    ('2.000850', 'cấp giấy phép lái xe'),
    ('2.001682', 'đăng ký kinh doanh hộ cá thể'),
]

async def search_procedure(page, query):
    url = f'https://dichvucong.gov.vn/p/home/dvc-tim-kiem-thu-tuc.html?key={query}'
    print(f'  Loading: {url[:80]}')
    
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
    except Exception as e:
        print(f'  Goto error: {e}')
        return []
    
    # Wait for either results selector or a timeout
    try:
        await page.wait_for_selector('a[href*="ma_thu_tuc"]', timeout=10000)
        print('  ✓ Found ma_thu_tuc links')
    except:
        print('  ✗ Timeout waiting for ma_thu_tuc links')
    
    # Use page.evaluate to query DOM - this runs in the browser
    result = await page.evaluate('''() => {
        // Get all links with ma_thu_tuc
        const links = Array.from(document.querySelectorAll('a[href*="ma_thu_tuc"]'));
        
        // Also check for text content nearby
        const items = [];
        for (const link of links) {
            const href = link.getAttribute('href') || '';
            const text = link.textContent.trim().substring(0, 80);
            const parent = link.closest('tr, li, div.item, div.row') || link.parentElement;
            const parentText = parent ? parent.textContent.trim().substring(0, 100) : '';
            // Extract ma_thu_tuc from href
            const match = href.match(/ma_thu_tuc=([^&]+)/);
            const code = match ? match[1] : '';
            items.push({code, text, href, parentText});
        }
        
        // Also look for any text containing X.XXXXXX pattern
        const allText = document.body ? document.body.innerHTML : '';
        const codeMatches = allText.match(/\\b[12]\\.[0-9]{6}\\b/g) || [];
        const uniqueCodes = [...new Set(codeMatches)];
        
        return {links: items, codes: uniqueCodes};
    }''')
    
    return result

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        results = {}
        for code, query in WRONG_PROCEDURES:
            print(f'\n[{code}] Searching: {query}')
            result = await search_procedure(page, query.replace(' ', '+'))
            
            codes_found = result.get('codes', [])
            links_found = result.get('links', [])
            print(f'  Codes in DOM: {codes_found[:10]}')
            print(f'  Links with ma_thu_tuc: {len(links_found)}')
            for item in links_found[:5]:
                print(f'    → {item["code"]}: {item["text"][:60]}')
            
            results[code] = result
        
        await browser.close()
        print('\n=== SUMMARY ===')
        for code, res in results.items():
            print(f'{code}: codes={res.get("codes", [])[:5]}, links={len(res.get("links", []))}')

asyncio.run(main())
