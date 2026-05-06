"""Deduplicate form_templates by URL and limit to reasonable count."""
import psycopg2, json, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect(host='localhost', port=4321, dbname='hanhchinh_db', user='postgres', password='123')
cur = conn.cursor()
cur.execute('SELECT code, name, form_templates FROM procedures ORDER BY code')
rows = cur.fetchall()

updated = 0
for code, name, forms in rows:
    if not forms:
        continue
    
    # Deduplicate by URL AND by filename (keep first occurrence of each name)
    seen_urls = set()
    seen_names = set()
    deduped = []
    for f in forms:
        url = f.get('url', '')
        fname = f.get('name', '')
        if url not in seen_urls and fname not in seen_names:
            seen_urls.add(url)
            seen_names.add(fname)
            deduped.append(f)
    
    if len(deduped) != len(forms):
        print(f"[{code}] {name[:40]}: {len(forms)} → {len(deduped)} forms")
        cur.execute('UPDATE procedures SET form_templates = %s WHERE code = %s',
                    (json.dumps(deduped, ensure_ascii=False), code))
        updated += 1

conn.commit()
conn.close()
print(f"\nDeduped {updated} procedures.")
