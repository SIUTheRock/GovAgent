"""
Download each DVC file link to check its filename from Content-Disposition header.
This tells us if the file actually matches the procedure.
Also use Playwright to get the rendered page title for verification.
"""
import urllib.request
import urllib.parse
import re
import ssl

ctx = ssl._create_unverified_context()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# Results from verify_codes.py
CODE_LINKS = {
    '1.001057': ['3fecdc7d7a9a616d'],
    '1.001123': ['3fee7f883bba2076'],
    '1.001125': ['3fea35dbf6d41ad8'],
    '1.001229': ['3fda16b1cfaa0e7c'],
    '1.001640': ['3fd11c17112e15ce'],
    '1.003311': ['3fe7dab18d2d1d50'],
    '1.003453': ['3fe9ce7b1eb2cc24'],
    '1.003559': ['3fe592e5fdb1a34c'],
    '1.003670': ['3fda5d9ab27b300a'],
    '1.003820': ['3fa6c8e8b68d6300', '3fdcf83a03a25f3c'],
    '1.004621': ['3febe7dc7a7466bd'],
    '1.004792': ['3fcaaa9166bb8514', '3fed925b5530f58c'],
    '1.004850': ['3fe44ec265f2710a', '3fdc0f98d8549912'],
    '1.005100': ['3fc23d1e5cbba8c4', '3fe97d7e6f417d23', '3fe8c871164c4dab', '3fdd07aa6f1617fa'],
    '1.005300': ['3f7f36ac4b473b00'],
    '2.000850': ['3fe46109c42bceeb'],
    '2.001682': ['3fc135b0b86a5bc8'],
    '2.002400': ['3fd2c17784ffbec4'],
}

PROC_NAMES = {
    '1.001057': 'Cấp GCN QSD đất',
    '1.001123': 'Chuyển mục đích SD đất',
    '1.001125': 'Đăng ký sang tên',
    '1.001229': 'Đăng ký thường trú',
    '1.001640': 'Đăng ký khai sinh',
    '1.003311': 'Tách hộ khẩu',
    '1.003453': 'Cấp phiếu LLTP số 1',
    '1.003559': 'Xác nhận tình trạng hôn nhân',
    '1.003670': 'Đăng ký nhận nuôi con nuôi',
    '1.003820': 'Cấp GCN ATTP',
    '1.004621': 'Đăng ký thay đổi hộ tịch',
    '1.004792': 'Đăng ký khai tử',
    '1.004850': 'Cấp GPXD nhà ở',
    '1.005100': 'Cấp phép kinh doanh karaoke',
    '1.005300': 'Cấp phép lao động NN',
    '2.000850': 'Cấp GPLX',
    '2.001682': 'ĐKKD hộ cá thể',
    '2.002400': 'Cấp giấy khám sức khỏe',
}

def get_filename(ma_hex):
    url = f'https://csdl.dichvucong.gov.vn/web/jsp/download_file.jsp?ma={ma_hex}'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        r = urllib.request.urlopen(req, context=ctx, timeout=10)
        cd = r.headers.get('Content-Disposition', '')
        # Try RFC 5987 encoding first: filename*=UTF-8''...
        m = re.search(r"filename\*=UTF-8''(.+)", cd)
        if m:
            return urllib.parse.unquote(m.group(1))
        # Try regular filename=
        m = re.search(r'filename=["\']?([^"\';\r\n]+)', cd)
        if m:
            fn = m.group(1).strip()
            # Try to decode if it looks like ISO-8859-1 encoded Vietnamese
            try:
                fn = fn.encode('iso-8859-1').decode('utf-8')
            except:
                pass
            return fn
        return f'(no filename) size={r.headers.get("Content-Length","?")}'
    except Exception as e:
        return f'ERROR: {e}'

for code, mas in CODE_LINKS.items():
    name = PROC_NAMES.get(code, code)
    for ma in mas:
        fname = get_filename(ma)
        print(f'{code} [{name}] | {fname}')
