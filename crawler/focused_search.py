"""
Focused searches for procedures that didn't match well.
"""
import urllib.request
import urllib.parse
import json
import ssl

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

# Init session
opener.open(urllib.request.Request(
    'https://dichvucong.gov.vn/p/home/dvc-ket-qua-thu-tuc.html?originKey=test&tukhoa=test&tinh_thanh=',
    headers={'User-Agent': HEADERS['User-Agent']}
), timeout=10)

def search(keyword, n=15):
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
    print(f"\n--- [{label}] Searching: '{keyword}' ---")
    docs = search(keyword, n)
    if docs:
        for d in docs:
            print(f"  [{d['ma_thu_tuc']}] {d.get('ten_thu_tuc','')[:75]}")
    else:
        print("  No results")

# Problem cases
show('1.001057', 'cấp giấy chứng nhận quyền sử dụng đất', 15)
show('1.001057b', 'đăng ký quyền sử dụng đất quyền sở hữu nhà ở', 10)
show('1.001123', 'chuyển mục đích sử dụng đất', 10)
show('1.001125', 'đăng ký biến động quyền sử dụng đất chuyển nhượng', 10)
show('1.001125b', 'sang tên quyền sử dụng đất', 10)
show('1.003311', 'tách hộ', 10)
show('1.003311b', 'tách hộ khẩu', 10)
show('1.003453', 'phiếu lý lịch tư pháp số 1', 10)
show('1.003454', 'phiếu lý lịch tư pháp số 2', 10)
show('1.003670', 'nhận nuôi con nuôi trong nước', 10)
show('1.004621', 'thay đổi cải chính hộ tịch', 10)
show('1.004700', 'xác nhận hộ nghèo', 10)
show('1.004850', 'cấp giấy phép xây dựng nhà ở riêng lẻ', 10)
show('1.005200', 'đăng ký nhãn hiệu hàng hóa', 10)
show('1.005200b', 'bảo hộ nhãn hiệu', 10)
show('1.005300', 'giấy phép lao động người nước ngoài', 10)
show('2.000850', 'cấp giấy phép lái xe', 10)
show('2.000850B', 'cấp lại giấy phép lái xe', 10)
show('2.002400', 'khám sức khỏe', 10)
show('2.002400b', 'cấp giấy chứng nhận sức khỏe', 10)
