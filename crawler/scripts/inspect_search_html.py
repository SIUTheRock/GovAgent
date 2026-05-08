"""Read saved search HTML and inspect its JS"""
import re

with open('E:/PPNCKH/crawler/data/search_Dang_ky_khai_s.html', encoding='utf-8') as f:
    html = f.read()

print('Size:', len(html))

# Extract inline scripts
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f'Found {len(scripts)} inline scripts')

for i, s in enumerate(scripts):
    s = s.strip()
    if s and len(s) > 50:
        # Look for API related code
        if any(kw in s for kw in ['initApi', 'rest.jsp', 'tthc', 'tim_kiem', 'search', 'executeQuery', 'AjaxJson']):
            print(f'\n--- Script {i} (API related) ---')
            print(s[:2000])

# External JS files
ext_scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
print('\n--- External scripts ---')
for s in ext_scripts:
    print(s)
