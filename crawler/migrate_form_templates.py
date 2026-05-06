import psycopg2, os
conn = psycopg2.connect("postgresql://postgres:123@localhost:4321/hanhchinh_db")
cur = conn.cursor()
cur.execute("ALTER TABLE procedures ADD COLUMN IF NOT EXISTS form_templates JSONB DEFAULT '[]'::jsonb")
conn.commit()
cur.close()
conn.close()
print("Migration done.")
