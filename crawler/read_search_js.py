"""
Extract and show the full searchProcedure function from the saved DVC search page HTML.
"""
import re

with open('E:/PPNCKH/crawler/data/search_raw.html', encoding='utf-8') as f:
    html = f.read()

# Find the searchProcedure function and surrounding code
idx = html.find('searchProcedure')
if idx > -1:
    # Get more context
    segment = html[max(0, idx-200):idx+2000]
    # Clean up
    print("=== searchProcedure context ===")
    print(segment)

# Also look for the complete inline script that contains searchProcedure
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for i, s in enumerate(scripts):
    if 'searchProcedure' in s:
        print(f"\n=== Script {i} containing searchProcedure (full) ===")
        print(s[:5000])
        break

# Also look for rest.jsp calls
for kw in ['rest.jsp', 'executeQuery', 'AjaxJson', 'initApiService']:
    idx = html.find(kw)
    if idx > -1:
        print(f"\n=== '{kw}' context ===")
        print(html[max(0,idx-50):idx+300])
