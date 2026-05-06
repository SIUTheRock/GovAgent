"""
Try the discovered DVC API endpoints:
1. /jsp/procedure-typehead.jsp - typeahead endpoint
2. apiservice.AjaxJson (POST rest.jsp) with type=fts, source_data=thu_tuc_v1
"""
import urllib.request
import urllib.parse
import json
import ssl
import re

ctx = ssl._create_unverified_context()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Referer': 'https://dichvucong.gov.vn/',
}

def try_get(url, label=''):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        r = urllib.request.urlopen(req, context=ctx, timeout=10)
        body = r.read().decode('utf-8', 'replace')
        ct = r.headers.get('Content-Type', '')
        print(f"GET {label or url}")
        print(f"  → Status: {r.status}, CT: {ct[:50]}, Size: {len(body)}")
        print(f"  → Body: {body[:500]}")
        return body
    except Exception as e:
        print(f"GET {label or url} → ERROR: {e}")
        return None

def try_post_rest(payload, label=''):
    url = 'https://dichvucong.gov.vn/p/home/jsp/rest.jsp'
    try:
        data = ('params=' + urllib.parse.quote(json.dumps(payload))).encode()
        req = urllib.request.Request(url, data=data, headers={
            **HEADERS, 'Content-Type': 'application/x-www-form-urlencoded'
        })
        r = urllib.request.urlopen(req, context=ctx, timeout=10)
        body = r.read().decode('utf-8', 'replace')
        ct = r.headers.get('Content-Type', '')
        print(f"POST rest.jsp {label}: params={list(payload.keys())}")
        print(f"  → Status: {r.status}, CT: {ct[:50]}, Size: {len(body)}")
        if 'json' in ct or body.startswith('{') or body.startswith('['):
            print(f"  → JSON: {body[:600]}")
        else:
            print(f"  → HTML snippet: {body[:300]}")
        return body
    except Exception as e:
        print(f"POST rest.jsp {label} → ERROR: {e}")
        return None

kw = 'khai sinh'
print("=== Test 1: Typeahead endpoint ===")
# Try various path combinations  
paths = [
    f'https://dichvucong.gov.vn/jsp/procedure-typehead.jsp?keyword=al:"{kw}"~5',
    f'https://dichvucong.gov.vn/p/home/jsp/procedure-typehead.jsp?keyword=al:"{kw}"~5',
    f'https://csdl.dichvucong.gov.vn/web/jsp/procedure-typehead.jsp?keyword=al:"{kw}"~5',
    f'https://dichvucong.gov.vn/p/home/jsp/procedure-typehead.jsp?keyword={urllib.parse.quote(kw)}',
]
for p in paths:
    try_get(p, p.split('/p/home')[-1][:80])
    print()

print("\n=== Test 2: POST rest.jsp with FTS params ===")
payloads = [
    {"key_search": f'al:"{kw}"~5', "page_size": 10, "start_row": 0, "source_data": "thu_tuc_v1", "type": "fts"},
    {"key_search": kw, "page_size": 10, "start_row": 0, "source_data": "thu_tuc_v1", "type": "fts"},
    {"ten_thu_tuc": kw, "source_data": "thu_tuc_v1", "type": "fts", "page_size": 10, "start_row": 0},
    {"key_search": kw, "source_data": "thu_tuc_v1"},
]
for p in payloads:
    try_post_rest(p)
    print()

print("\n=== Test 3: Fetch results page HTML ===")
url = f'https://dichvucong.gov.vn/p/home/dvc-ket-qua-thu-tuc.html?originKey={urllib.parse.quote(kw)}&tukhoa={urllib.parse.quote(kw)}&tinh_thanh='
body = try_get(url, 'dvc-ket-qua-thu-tuc.html')
if body:
    # Save it
    with open('E:/PPNCKH/crawler/data/results_page.html', 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"  Saved {len(body)} bytes to data/results_page.html")
    # Look for procedure codes
    codes = re.findall(r'\b[12]\.[0-9]{6}\b', body)
    print(f"  Procedure codes found: {codes[:10]}")
    # Look for ma_thu_tuc links
    links = re.findall(r'ma_thu_tuc=([^&"\'\\s]+)', body)
    print(f"  ma_thu_tuc params: {links[:10]}")
