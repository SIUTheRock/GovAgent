import json
with open('E:/PPNCKH/crawler/data/procedures_raw.json', encoding='utf-8') as f:
    data = json.load(f)
print(f'Total: {len(data)} procedures')
print()
for p in data:
    code = p['code']
    name = p['name'][:45]
    url = p.get('source_url', '')
    print(f'{code:14} | {name:45} | {url[-20:]}')
