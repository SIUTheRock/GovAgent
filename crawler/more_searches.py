"""More focused searches for remaining hard cases."""
import urllib.request
import urllib.parse
import json
import ssl

ctx = ssl._create_unverified_context()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://dichvucong.gov.vn/p/home/dvc-ket-qua-thu-tuc.html',
}

opener.open(urllib.request.Request(
    'https://dichvucong.gov.vn/p/home/dvc-ket-qua-thu-tuc.html?originKey=test&tukhoa=test&tinh_thanh=',
    headers={'User-Agent': HEADERS['User-Agent']}
), timeout=10)

def search(keyword, n=10):
    words = keyword.strip().split()
    key_search = f'"{keyword}"^8 OR "{keyword}"~5' if len(words) > 2 else f'"{keyword}"'
    payload = {"type": "fts", "key_search": key_search, "source_data": "thu_tuc_v1", "page_size": str(n), "start_row": "0"}
    body = ('params=' + urllib.parse.quote(json.dumps(payload))).encode('utf-8')
    req = urllib.request.Request('https://dichvucong.gov.vn/jsp/rest.jsp', data=body, headers=HEADERS)
    r = opener.open(req, timeout=15)
    resp = json.loads(r.read().decode('utf-8', 'replace'))
    if resp and 'response' in resp:
        return resp['response'].get('docs', [])
    return []

def show(label, keyword, n=10):
    print(f"\n--- [{label}] '{keyword}' ---")
    docs = search(keyword, n)
    for d in docs:
        print(f"  [{d['ma_thu_tuc']}] {d.get('ten_thu_tuc','')[:80]}")
    if not docs:
        print("  No results")

# 1.001125 - Đăng ký sang tên (chuyển nhượng quyền sử dụng đất)
show('1.001125a', 'biến động chuyển nhượng quyền sử dụng đất')
show('1.001125b', 'chuyển nhượng quyền sử dụng đất')
show('1.001125c', 'đăng ký biến động đất đai')

# 1.001123 - Chuyển mục đích sử dụng đất (xin phép)
show('1.001123', 'cho phép chuyển mục đích sử dụng đất')

# 1.003670 - Đăng ký nhận nuôi con nuôi trong nước
show('1.003670a', 'đăng ký nuôi con nuôi')
show('1.003670b', 'con nuôi trong nước')

# 1.004700 - Xác nhận hộ nghèo, hộ cận nghèo
show('1.004700a', 'hộ nghèo cận nghèo')
show('1.004700b', 'giấy xác nhận hộ nghèo')
show('1.004700c', 'hộ nghèo')

# 1.004850 - Cấp GPXD nhà ở riêng lẻ
show('1.004850a', 'cấp giấy phép xây dựng')
show('1.004850b', 'giấy phép xây dựng nhà ở')

# 1.005200 - Đăng ký bảo hộ nhãn hiệu
show('1.005200a', 'nhãn hiệu')
show('1.005200b', 'đăng ký nhãn hiệu')
show('1.005200c', 'nhãn hiệu hàng hóa')

# 2.002400 - Cấp giấy khám sức khỏe
show('2.002400a', 'giấy khám sức khỏe')
show('2.002400b', 'sức khỏe')
show('2.002400c', 'khám sức khoẻ')
