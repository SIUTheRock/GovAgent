"""
Search DVC for all 30 procedures and find their correct ma_thu_tuc codes.
Uses the working FTS API: POST https://dichvucong.gov.vn/jsp/rest.jsp
"""
import urllib.request
import urllib.parse
import json
import ssl
import re
import psycopg2

ctx = ssl._create_unverified_context()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://dichvucong.gov.vn',
    'Referer': 'https://dichvucong.gov.vn/p/home/dvc-ket-qua-thu-tuc.html?originKey=test&tukhoa=test&tinh_thanh=',
}

def search_dvc(keyword, page_size=20):
    words = keyword.strip().split()
    if len(words) > 2:
        key_search = f'"{keyword}"^8 OR "{keyword}"~5'
    else:
        key_search = f'"{keyword}"'
    
    payload = {
        "type": "fts",
        "key_search": key_search,
        "source_data": "thu_tuc_v1",
        "page_size": str(page_size),
        "start_row": "0",
    }
    
    body = ('params=' + urllib.parse.quote(json.dumps(payload))).encode('utf-8')
    
    try:
        req = urllib.request.Request('https://dichvucong.gov.vn/jsp/rest.jsp', data=body, headers=HEADERS)
        r = opener.open(req, timeout=15)
        response_body = r.read().decode('utf-8', 'replace')
        ct = r.headers.get('Content-Type', '')
        if 'json' in ct:
            data = json.loads(response_body)
            if isinstance(data, dict) and 'response' in data:
                return data['response'].get('docs', [])
    except Exception as e:
        print(f"  ERROR: {e}")
    return []

def normalize(s):
    """Normalize Vietnamese text for comparison"""
    # Remove common prefix words
    s = s.lower()
    for prefix in ['thủ tục ', 'thủ tuc ', 'thu tuc ']:
        if s.startswith(prefix):
            s = s[len(prefix):]
    return s

# Init session
try:
    opener.open(urllib.request.Request(
        'https://dichvucong.gov.vn/p/home/dvc-ket-qua-thu-tuc.html?originKey=test&tukhoa=test&tinh_thanh=',
        headers={'User-Agent': HEADERS['User-Agent']}
    ), timeout=10)
except: pass

# Get all procedures from DB
conn = psycopg2.connect(host='localhost', port=4321, dbname='hanhchinh_db', user='postgres', password='123')
cur = conn.cursor()
cur.execute('SELECT code, name FROM procedures ORDER BY code')
procedures = cur.fetchall()
conn.close()

# For each procedure, search DVC and find best match
print(f"Searching {len(procedures)} procedures...\n")
results = {}

for code, name in procedures:
    print(f"\n[{code}] {name[:50]}")
    
    # Try different search queries
    docs = search_dvc(name)
    
    if not docs:
        # Try shorter query
        words = name.split()[:4]
        docs = search_dvc(' '.join(words))
    
    if docs:
        name_norm = normalize(name)
        best_match = None
        best_score = -1
        
        for doc in docs:
            dvc_name = doc.get('ten_thu_tuc', '')
            dvc_code = doc.get('ma_thu_tuc', '')
            dvc_norm = normalize(dvc_name)
            
            # Score by substring match
            score = 0
            if name_norm in dvc_norm or dvc_norm in name_norm:
                score = 3
            else:
                # Count shared words
                name_words = set(name_norm.split())
                dvc_words = set(dvc_norm.split())
                shared = name_words & dvc_words
                score = len(shared) / max(len(name_words), len(dvc_words))
            
            if score > best_score:
                best_score = score
                best_match = doc
        
        if best_match:
            dvc_code = best_match.get('ma_thu_tuc', '')
            dvc_name = best_match.get('ten_thu_tuc', '')
            match_flag = "✓" if best_score >= 0.5 else "?"
            print(f"  {match_flag} Best: [{dvc_code}] {dvc_name[:60]} (score={best_score:.2f})")
            
            # Show top 3 results for reference
            for d in docs[:3]:
                marker = ">>>" if d['ma_thu_tuc'] == dvc_code else "   "
                print(f"  {marker} [{d['ma_thu_tuc']}] {d.get('ten_thu_tuc','')[:60]}")
            
            results[code] = {
                'name': name,
                'dvc_code': dvc_code,
                'dvc_name': dvc_name,
                'score': best_score,
                'all_results': [(d['ma_thu_tuc'], d.get('ten_thu_tuc','')[:60]) for d in docs[:5]]
            }
    else:
        print(f"  No results found")
        results[code] = {'name': name, 'dvc_code': None, 'dvc_name': None, 'score': 0}

# Save results
with open('E:/PPNCKH/crawler/data/dvc_code_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n\n=== FINAL MAPPING ===")
print(f"{'App Code':<15} {'App Name':<45} {'DVC Code':<15} {'Match'}")
print("-" * 100)
for code, r in results.items():
    flag = "✓" if r.get('score', 0) >= 0.5 else "?"
    print(f"{code:<15} {r['name'][:44]:<45} {str(r.get('dvc_code','?')):<15} {flag} {r.get('dvc_name','?')[:40]}")

print(f"\nSaved to data/dvc_code_mapping.json")
