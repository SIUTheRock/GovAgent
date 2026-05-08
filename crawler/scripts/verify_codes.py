"""
Fetch raw HTML from DVC for each procedure code and look at what download_file links appear.
This will tell us what files DVC actually has for each code, helping us determine correctness.
Also try to extract the procedure title from the page.
"""
import urllib.request
import re
import ssl
import psycopg2
import json

ctx = ssl._create_unverified_context()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

conn = psycopg2.connect(host='localhost', port=4321, dbname='hanhchinh_db', 
                        user='postgres', password='123')
cur = conn.cursor()
cur.execute('SELECT code, name FROM procedures ORDER BY code')
rows = cur.fetchall()
conn.close()

FAKE_MAP = {
    '1.004850A': '1.004850',
    '2.001682A': '2.001682',
    '2.000850A': '2.000850',
    '2.000850B': '2.000850',
}

def fetch_dvc(ma_thu_tuc):
    url = f'https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc={ma_thu_tuc}'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        r = urllib.request.urlopen(req, context=ctx, timeout=10)
        return r.read().decode('utf-8', 'replace')
    except Exception as e:
        return f'ERROR: {e}'

for code, name in rows:
    dvc_code = FAKE_MAP.get(code, code)
    html = fetch_dvc(dvc_code)
    if html.startswith('ERROR'):
        print(f'{code}: {name[:40]} → {html}')
        continue
    
    # Extract download links
    links = re.findall(r'download_file\.jsp\?ma=([a-f0-9]+)', html)
    # Extract file names associated with download links
    # Pattern: download_file.jsp?ma=... <something> "filename"
    all_forms = re.findall(r'download_file\.jsp\?ma=([a-f0-9]+)[^"]*"[^"]*"[^>]*>([^<]{3,60})', html)
    # Try getting name from title/h1 area
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    h1 = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()[:60] if h1_match else ''
    
    print(f'{code}: {name[:40]:<40} | DVC links: {links} | H1: {h1[:50]}')
