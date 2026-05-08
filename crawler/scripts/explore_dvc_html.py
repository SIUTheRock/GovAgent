"""
Save raw HTML of DVC pages to understand structure.
Also try to call csdl API directly.
"""
import urllib.request
import urllib.parse
import ssl
import re
import json

ctx = ssl._create_unverified_context()
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    r = urllib.request.urlopen(req, context=ctx, timeout=15)
    return r.read().decode('utf-8', 'replace')

# Save full HTML of 1.001640
html = fetch('https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001640')
with open('E:/PPNCKH/crawler/data/page_1001640.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved page_1001640.html, size:', len(html))

# Extract all ma_thu_tuc values
codes = re.findall(r'ma_thu_tuc=([0-9A-Z.]+)', html)
print('Procedure codes found in HTML:', list(set(codes)))

# Extract all download links
dl_links = re.findall(r'href="(https?://csdl\.dichvucong\.gov\.vn/web/jsp/download_file\.jsp\?ma=[0-9a-f]+)"', html)
print('Download links:', dl_links)

# Also get the page of 1.001057 (wrongly mapped)
html2 = fetch('https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001057')
with open('E:/PPNCKH/crawler/data/page_1001057.html', 'w', encoding='utf-8') as f:
    f.write(html2)
print('\nSaved page_1001057.html, size:', len(html2))

dl_links2 = re.findall(r'href="(https?://csdl\.dichvucong\.gov\.vn/web/jsp/download_file\.jsp\?ma=[0-9a-f]+)"', html2)
print('Download links for 1.001057:', dl_links2)

# Now try csdl API
print('\n--- Trying csdl REST API ---')
api_url = 'https://csdl.dichvucong.gov.vn/web/jsp/rest.jsp'
# Try search by keyword
test_payloads = [
    {"pageIndex": 1, "pageSize": 5, "keyword": "khai sinh"},
    {"pageIndex": 1, "pageSize": 5, "tuKhoa": "khai sinh"},
    {"key": "khai sinh", "pageIndex": 1, "pageSize": 5},
]
for payload in test_payloads:
    try:
        data = ('params=' + urllib.parse.quote(json.dumps(payload))).encode()
        req = urllib.request.Request(api_url, data=data, headers={
            **HEADERS, 'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://dichvucong.gov.vn/'
        }, method='POST')
        r = urllib.request.urlopen(req, context=ctx, timeout=10)
        resp = r.read().decode('utf-8', 'replace')
        print(f'Payload {list(payload.keys())}: {resp[:300]}')
    except Exception as e:
        print(f'Payload {list(payload.keys())} error: {e}')
