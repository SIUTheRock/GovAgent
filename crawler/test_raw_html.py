"""Test if DVC detail page is server-side rendered by checking raw HTML"""
import urllib.request
import ssl
import re

ctx = ssl._create_unverified_context()

req = urllib.request.Request(
    'https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001640',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
)
r = urllib.request.urlopen(req, context=ctx, timeout=15)
c = r.read().decode('utf-8', 'replace')

print('Size:', len(c))
print('download_file in raw HTML:', 'download_file' in c)
print('khai sinh in raw HTML:', 'khai sinh' in c.lower())
print('Đăng ký khai sinh in raw HTML:', 'Đăng ký khai sinh' in c)

if 'download_file' in c:
    matches = re.findall(r'download_file[^\s"\'<>]{5,80}', c)
    print('Download links:', matches[:5])

# Also look for csdl references
csdl_refs = re.findall(r'csdl\.dichvucong[^\s"\'<>]{5,60}', c)
print('CSDL refs:', csdl_refs[:5])

# Look for iframes
iframes = re.findall(r'<iframe[^>]+>', c)
print('Iframes:', iframes[:3])

# Look for rest.jsp calls in inline scripts
rest_calls = re.findall(r'rest\.jsp[^\s"\'<>]{0,60}', c)
print('rest.jsp refs:', rest_calls[:5])

# Print 500 chars around first script tag referencing ma_thu_tuc
idx = c.find('ma_thu_tuc')
if idx > -1:
    print('\nContext around ma_thu_tuc:')
    print(c[max(0, idx-100):idx+200])
