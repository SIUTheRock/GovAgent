"""Try various API endpoints on csdl.dichvucong.gov.vn"""
import urllib.request
import urllib.parse
import ssl
import json

ctx = ssl._create_unverified_context()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://dichvucong.gov.vn/',
    'Origin': 'https://dichvucong.gov.vn',
}

def try_get(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        r = urllib.request.urlopen(req, context=ctx, timeout=8)
        body = r.read().decode('utf-8', 'replace')
        ct = r.headers.get('Content-Type', '')
        print(f"GET {url}")
        print(f"  → Status: {r.status}, CT: {ct[:40]}, Size: {len(body)}")
        if 'json' in ct or body.startswith('[') or body.startswith('{'):
            print(f"  → JSON: {body[:300]}")
        return body
    except Exception as e:
        print(f"GET {url} → {type(e).__name__}: {e}")
        return None

def try_post(url, payload):
    try:
        data = ('params=' + urllib.parse.quote(json.dumps(payload))).encode()
        req = urllib.request.Request(url, data=data, headers={
            **HEADERS, 'Content-Type': 'application/x-www-form-urlencoded'
        })
        r = urllib.request.urlopen(req, context=ctx, timeout=8)
        body = r.read().decode('utf-8', 'replace')
        ct = r.headers.get('Content-Type', '')
        print(f"POST {url} params={list(payload.keys())}")
        print(f"  → Status: {r.status}, CT: {ct[:40]}, Size: {len(body)}")
        if 'json' in ct or body.startswith('[') or body.startswith('{'):
            print(f"  → JSON: {body[:400]}")
        return body
    except Exception as e:
        print(f"POST {url} → {type(e).__name__}: {e}")
        return None

print("=== Testing CSDL GET endpoints ===")
base = 'https://csdl.dichvucong.gov.vn'
endpoints = [
    f'{base}/web/api/tthc/tim-kiem?keyword=khai+sinh&pageIndex=1&pageSize=5',
    f'{base}/web/api/tthc/search?keyword=khai+sinh',
    f'{base}/web/api/search?keyword=khai+sinh',
    f'{base}/web/api/procedure/search?keyword=khai+sinh',
    f'{base}/web/rest/tthc?keyword=khai+sinh',
    f'{base}/web/api/tthc?ma_thu_tuc=1.001640',
]
for ep in endpoints:
    try_get(ep)

print("\n=== Testing CSDL POST endpoints ===")
post_payloads = [
    {"keyword": "khai sinh", "pageIndex": 1, "pageSize": 5},
    {"ten_tthc": "khai sinh", "pageIndex": 1, "pageSize": 5},
    {"search": "khai sinh", "page": 1, "size": 5},
    {"ma_thu_tuc": "1.001640"},
    {"ten": "khai sinh"},
]
for p in post_payloads:
    try_post(f'{base}/web/jsp/rest.jsp', p)
