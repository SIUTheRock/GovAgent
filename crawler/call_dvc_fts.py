"""
Call DVC search API correctly:
- URL: https://dichvucong.gov.vn/jsp/rest.jsp  (root-relative /jsp/rest.jsp)
- Method: POST
- Body: params=<JSON string> (x-www-form-urlencoded)
- JSON payload: {type:"fts", key_search:"\"khai sinh\"", source_data:"thu_tuc_v1", page_size:"10", start_row:"0"}
"""
import urllib.request
import urllib.parse
import json
import ssl
import re

ctx = ssl._create_unverified_context()

# Need a session to simulate browser context
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://dichvucong.gov.vn',
    'Referer': 'https://dichvucong.gov.vn/p/home/dvc-ket-qua-thu-tuc.html?originKey=khai+sinh&tukhoa=khai+sinh&tinh_thanh=',
}

def search_dvc(keyword):
    # Determine key_search format based on word count
    words = keyword.strip().split()
    if len(words) > 2:
        key_search = f'"{keyword}"^8 OR "{keyword}"~5'
    else:
        key_search = f'"{keyword}"'
    
    payload = {
        "type": "fts",
        "key_search": key_search,
        "source_data": "thu_tuc_v1",
        "page_size": "20",
        "start_row": "0",
    }
    
    body = ('params=' + urllib.parse.quote(json.dumps(payload))).encode('utf-8')
    
    urls_to_try = [
        'https://dichvucong.gov.vn/jsp/rest.jsp',
        'https://dichvucong.gov.vn/p/home/jsp/rest.jsp',
        'https://csdl.dichvucong.gov.vn/web/jsp/rest.jsp',
    ]
    
    for url in urls_to_try:
        try:
            req = urllib.request.Request(url, data=body, headers=HEADERS)
            r = opener.open(req, timeout=10)
            response_body = r.read().decode('utf-8', 'replace')
            ct = r.headers.get('Content-Type', '')
            print(f"POST {url}")
            print(f"  → Status: {r.status}, CT: {ct[:60]}, Size: {len(response_body)}")
            
            if 'json' in ct:
                try:
                    data = json.loads(response_body)
                    if isinstance(data, dict) and 'response' in data:
                        docs = data['response'].get('docs', [])
                        print(f"  → SUCCESS! Found {len(docs)} results:")
                        for d in docs[:5]:
                            print(f"    {d.get('ma_thu_tuc','?')}: {d.get('ten_thu_tuc','?')[:70]}")
                        return docs
                    else:
                        print(f"  → JSON but unexpected format: {str(data)[:200]}")
                except:
                    print(f"  → JSON parse error. Body: {response_body[:300]}")
            else:
                print(f"  → Body preview: {response_body[:200]}")
        except Exception as e:
            print(f"POST {url} → {type(e).__name__}: {e}")
    
    return []

# First get session cookies by visiting the page
print("=== Getting session cookies ===")
try:
    req = urllib.request.Request(
        'https://dichvucong.gov.vn/p/home/dvc-ket-qua-thu-tuc.html?originKey=khai+sinh&tukhoa=khai+sinh&tinh_thanh=',
        headers={'User-Agent': HEADERS['User-Agent']}
    )
    r = opener.open(req, timeout=10)
    print(f"Session page status: {r.status}")
except Exception as e:
    print(f"Session page error: {e}")

print("\n=== Test searches ===")
tests = [
    "khai sinh",
    "khai tử",
    "cấp giấy phép lái xe",
    "đăng ký kinh doanh hộ cá thể",
]
for kw in tests:
    print(f"\nSearching: '{kw}'")
    results = search_dvc(kw)
    if results:
        print("FOUND!")
        break
