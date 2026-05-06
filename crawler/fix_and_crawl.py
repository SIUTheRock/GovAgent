"""
Complete fix for DVC codes and form_templates.
Steps:
1. Maps each app procedure code to correct DVC code
2. Fetches raw DVC HTML for each (using urllib - fast, no Playwright)
3. Extracts download links
4. Gets actual filenames from Content-Disposition headers
5. Updates form_templates in DB

For procedures with no forms on DVC (returns 0 links), falls back to portal link.
"""
import urllib.request
import urllib.parse
import re
import ssl
import json
import psycopg2
from time import sleep

ctx = ssl._create_unverified_context()
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Mapping: app_code → correct_dvc_code
# None means no DVC procedure found (use portal link)
DVC_CODE_MAP = {
    '1.001057':  '1.012787',   # Cấp GCN QSD đất → Đăng ký, cấp GCN quyền sử dụng đất
    '1.001064':  '2.000635',   # Cấp bản sao trích lục hộ tịch
    '1.001123':  '1.013992',   # Chuyển mục đích SD đất
    '1.001125':  '1.013831',   # Đăng ký sang tên (biến động chuyển nhượng)
    '1.001229':  '1.004222',   # Đăng ký thường trú
    '1.001640':  '1.001193',   # Đăng ký khai sinh
    '1.003306':  '1.004194',   # Đăng ký tạm trú
    '1.003311':  '1.010038',   # Tách hộ
    '1.003453':  '3.000333',   # Cấp phiếu LLTP số 1
    '1.003454':  '3.000334',   # Cấp phiếu LLTP số 2
    '1.003559':  '1.004873',   # Xác nhận tình trạng hôn nhân
    '1.003670':  '2.001263',   # Đăng ký nhận nuôi con nuôi trong nước
    '1.003820':  '2.001827',   # Cấp GCN ATTP
    '1.004621':  '1.004859',   # Đăng ký thay đổi, cải chính hộ tịch
    '1.004700':  '1.011607',   # Xác nhận hộ nghèo, hộ cận nghèo
    '1.004734':  '1.000894',   # Đăng ký kết hôn
    '1.004792':  '1.000656',   # Đăng ký khai tử
    '1.004800':  '1.004884',   # Đăng ký lại khai sinh
    '1.004850':  '1.009122',   # Cấp GPXD nhà ở riêng lẻ
    '1.004850A': '1.013226',   # Điều chỉnh GPXD
    '1.005000':  '1.014748',   # Hưởng trợ cấp thất nghiệp
    '1.005100':  '1.001029',   # Cấp phép kinh doanh karaoke
    '1.005200':  '1.015002',   # Đăng ký nhãn hiệu hàng hóa
    '1.005300':  '1.014199',   # Cấp GPLĐ người nước ngoài
    '2.000850':  '3.000346',   # Cấp GPLX
    '2.000850A': '3.000347',   # Đổi GPLX
    '2.000850B': '3.000348',   # Cấp lại GPLX bị mất
    '2.001682':  '1.001612',   # Đăng ký thành lập hộ kinh doanh
    '2.001682A': '2.000720',   # Thay đổi đăng ký hộ kinh doanh
    '2.002400':  None,         # Cấp giấy khám sức khỏe (not in DVC)
}

DVC_BASE = 'https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html'
CSDL_BASE = 'https://csdl.dichvucong.gov.vn/web/jsp/download_file.jsp'
PORTAL_FALLBACK = {
    'url': 'https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html',
    'name': 'Xem mẫu đơn và tải về trên Cổng Dịch vụ công',
    'code': 'dichvucong.gov.vn'
}

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        r = urllib.request.urlopen(req, context=ctx, timeout=12)
        return r.read().decode('utf-8', 'replace')
    except Exception as e:
        return None

def get_filename(ma_hex):
    url = f'{CSDL_BASE}?ma={ma_hex}'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        r = urllib.request.urlopen(req, context=ctx, timeout=10)
        cd = r.headers.get('Content-Disposition', '')
        # Try RFC 5987 encoding
        m = re.search(r"filename\*=UTF-8''(.+)", cd)
        if m:
            return urllib.parse.unquote(m.group(1))
        # Regular filename
        m = re.search(r'filename=["\']?([^"\';\r\n]+)', cd)
        if m:
            fn = m.group(1).strip()
            try:
                fn = fn.encode('iso-8859-1').decode('utf-8')
            except:
                pass
            return fn
        return None
    except Exception as e:
        return None

def get_forms_for_dvc_code(dvc_code):
    """Fetch DVC page and extract download links with filenames."""
    url = f'{DVC_BASE}?ma_thu_tuc={dvc_code}'
    html = fetch_html(url)
    if not html:
        return None
    
    # Extract download file hex codes
    mas = re.findall(r'download_file\.jsp\?ma=([a-f0-9]+)', html)
    if not mas:
        return []
    
    forms = []
    for ma in mas:
        fname = get_filename(ma)
        if fname:
            full_url = f'{CSDL_BASE}?ma={ma}'
            forms.append({
                'name': fname,
                'url': full_url,
                'code': 'download'
            })
    return forms

# Connect to DB
conn = psycopg2.connect(host='localhost', port=4321, dbname='hanhchinh_db', user='postgres', password='123')
cur = conn.cursor()
cur.execute('SELECT code, name FROM procedures ORDER BY code')
procedures = cur.fetchall()

print(f"Processing {len(procedures)} procedures...\n")
results = {}

for app_code, name in procedures:
    dvc_code = DVC_CODE_MAP.get(app_code)
    
    if dvc_code is None:
        # No DVC mapping - use portal link with the app code for URL
        portal = dict(PORTAL_FALLBACK)
        portal['url'] = f'{DVC_BASE}?ma_thu_tuc={app_code}'
        forms = [portal]
        status = 'PORTAL (no DVC code)'
    else:
        forms = get_forms_for_dvc_code(dvc_code)
        
        if forms is None:
            portal = dict(PORTAL_FALLBACK)
            portal['url'] = f'{DVC_BASE}?ma_thu_tuc={dvc_code}'
            forms = [portal]
            status = 'PORTAL (fetch failed)'
        elif len(forms) == 0:
            portal = dict(PORTAL_FALLBACK)
            portal['url'] = f'{DVC_BASE}?ma_thu_tuc={dvc_code}'
            forms = [portal]
            status = 'PORTAL (no download links)'
        else:
            status = f'OK ({len(forms)} forms)'
    
    results[app_code] = forms
    file_info = [(f['name'][:35], 'D' if 'download_file' in f.get('url','') else 'P') for f in forms]
    print(f"[{app_code}] {name[:45]:<45} | {status}")
    for fn, t in file_info:
        print(f"  {'📄' if t=='D' else '🌐'} {fn}")
    
    sleep(0.3)  # Rate limit

print("\n\n=== Updating database ===")
updated = 0
for app_code, forms in results.items():
    try:
        cur.execute(
            'UPDATE procedures SET form_templates = %s WHERE code = %s',
            (json.dumps(forms, ensure_ascii=False), app_code)
        )
        updated += 1
    except Exception as e:
        print(f"  ERROR updating {app_code}: {e}")
        conn.rollback()

conn.commit()
conn.close()
print(f"Updated {updated}/{len(procedures)} procedures in database.")
print("\nDone! Run check_db.py to verify.")
