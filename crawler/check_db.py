import psycopg2, json, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = psycopg2.connect(host='localhost', port=4321, dbname='hanhchinh_db', user='postgres', password='123')
cur = conn.cursor()
cur.execute('SELECT code, name, form_templates FROM procedures ORDER BY code')
rows = cur.fetchall()
for code, name, fts in rows:
    fts_info = []
    if fts:
        for ft in fts:
            url = ft.get('url','')
            is_direct = 'download_file.jsp' in url
            fts_info.append(('D' if is_direct else 'P', ft.get('name','')[:30]))
    print(f'{code}: {name[:45]:<45} | {fts_info}')
conn.close()
