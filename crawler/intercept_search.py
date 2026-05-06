"""Intercept XHR/fetch on DVC search page to find the real API endpoint"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        
        captured = []
        
        async def on_request(req):
            url = req.url
            # Only capture XHR / fetch
            rt = req.resource_type
            if rt in ('xhr', 'fetch') or 'rest.jsp' in url or 'api' in url.lower():
                captured.append({'type': rt, 'method': req.method, 'url': url})
        
        async def on_response(resp):
            url = resp.url
            if 'rest.jsp' in url or ('api' in url.lower() and 'dichvucong' in url):
                try:
                    body = await resp.text()
                    print(f"RESPONSE: {resp.status} {url}")
                    print(f"  Body: {body[:300]}")
                except:
                    pass

        page.on('request', on_request)
        page.on('response', on_response)

        # Load search page WITHOUT key param first
        print("Loading search page (no key)...")
        await page.goto('https://dichvucong.gov.vn/p/home/dvc-tim-kiem-thu-tuc.html', 
                       wait_until='domcontentloaded', timeout=15000)
        await asyncio.sleep(3)
        
        # Find inputs
        inputs = await page.query_selector_all('input')
        print(f"Found {len(inputs)} inputs")
        for inp in inputs:
            t = await inp.get_attribute('type')
            n = await inp.get_attribute('name')
            p2 = await inp.get_attribute('placeholder')
            print(f"  input type={t} name={n} placeholder={p2}")
        
        # Try finding search input
        search_input = None
        for sel in ['input[type=text]', 'input[name*=key]', 'input[placeholder*=tìm]', 
                    'input[placeholder*=Tìm]', 'input[placeholder*=search]', 
                    '.search-input', '#keyword', '#key', 'input[name=key]']:
            el = await page.query_selector(sel)
            if el:
                print(f"Found search input via: {sel}")
                search_input = el
                break
        
        if search_input:
            print("Typing in search input...")
            await search_input.type('Đăng ký khai sinh', delay=50)
            await asyncio.sleep(2)
            
            # Try pressing Enter
            await page.keyboard.press('Enter')
            await asyncio.sleep(5)
        else:
            print("No search input found on page.")
            print("Page title:", await page.title())
            # Try evaluate to find inputs
            all_inputs = await page.evaluate("""
                () => [...document.querySelectorAll('input, select, textarea')]
                    .map(el => ({tag: el.tagName, type: el.type, name: el.name, 
                                 placeholder: el.placeholder, id: el.id}))
            """)
            print(f"Evaluated inputs ({len(all_inputs)}):", all_inputs[:5])
        
        print(f"\n=== Captured {len(captured)} XHR/fetch requests ===")
        for c in captured:
            print(f"  [{c['type']}] {c['method']} {c['url']}")
        
        await browser.close()

asyncio.run(main())
