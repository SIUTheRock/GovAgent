"""
Fetch the DVC search page HTML with urllib (works unlike Playwright),
then find and download the JS files to locate the search API endpoint.
"""
import urllib.request
import urllib.parse
import re
import ssl
import json

ctx = ssl._create_unverified_context()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
}

def fetch(url, extra_headers=None):
    try:
        h = {**HEADERS, **(extra_headers or {})}
        req = urllib.request.Request(url, headers=h)
        r = urllib.request.urlopen(req, context=ctx, timeout=15)
        body = r.read().decode('utf-8', 'replace')
        return body, dict(r.headers)
    except Exception as e:
        return None, str(e)

BASE = 'https://dichvucong.gov.vn'

print("=== Step 1: Fetch search page HTML ===")
html, hdrs = fetch(f'{BASE}/p/home/dvc-tim-kiem-thu-tuc.html?key=khai+sinh')
if html:
    print(f"Got {len(html)} bytes")
    # Save for inspection
    with open('E:/PPNCKH/crawler/data/search_raw.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Saved to data/search_raw.html")
    
    # Find external JS references
    ext_scripts = re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', html)
    print(f"\nExternal scripts ({len(ext_scripts)}):")
    for s in ext_scripts:
        print(f"  {s}")
    
    # Check inline scripts for search API hints
    inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"\nInline scripts: {len(inline_scripts)}")
    for i, s in enumerate(inline_scripts):
        s = s.strip()
        if s and any(kw in s.lower() for kw in ['tim', 'search', 'api', 'ajax', 'rest', 'query', 'fetch']):
            print(f"\n--- Inline script {i} ---")
            print(s[:500])
    
    # Look for any Angular/jQuery app initialization
    for kw in ['ng-app', 'angular', 'timKiem', 'tim_kiem', 'searchKey', 'pageController', 'ng-controller']:
        if kw.lower() in html.lower():
            idx = html.lower().find(kw.lower())
            print(f"\nFound '{kw}': ...{html[max(0,idx-50):idx+100]}...")
else:
    print(f"Failed: {hdrs}")

print("\n=== Step 2: Fetch key JS files ===")
if html:
    # Focus on app JS files, not vendor libs
    for src in ext_scripts:
        if any(kw in src for kw in ['app', 'main', 'controller', 'service', 'tthc', 'tim', 'search']):
            full_url = src if src.startswith('http') else BASE + src
            print(f"\nFetching: {full_url[:100]}")
            js, _ = fetch(full_url)
            if js:
                print(f"  Size: {len(js)}")
                # Search for relevant functions
                for kw in ['timKiem', 'tim_kiem', 'searchTTHC', 'rest.jsp', 'executeQuery', 'key', 'pageIndex']:
                    if kw in js:
                        idx = js.find(kw)
                        print(f"  Found '{kw}': {js[max(0,idx-30):idx+100]}")
