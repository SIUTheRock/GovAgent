"""
Cập nhật mã thủ tục trong database PostgreSQL theo danh sách đã xác minh.
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:123@localhost:4321/hanhchinh_db"
DVC_BASE = "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc="

# (mã_cũ, mã_mới)
UPDATES = [
    # Nhóm 1: Mã có hậu tố A/B không chuẩn
    ("1.004850A", "1.013226"),
    ("2.000850A", "3.000347"),
    ("2.000850B", "3.000348"),
    ("2.001682A", "2.000720"),

    # Nhóm 2: Hộ tịch
    ("1.001640", "1.001193"),
    ("1.004734", "1.000894"),
    ("1.004792", "1.000656"),
    ("1.004800", "1.004884"),
    ("1.001064", "2.000635"),
    ("1.003559", "1.004873"),
    ("1.004621", "1.000881"),

    # Nhóm 3: Cư trú
    ("1.001229", "1.004222"),
    ("1.003306", "1.004194"),

    # Nhóm 4: Giao thông
    ("2.000850", "3.000346"),

    # Nhóm 5: Kinh doanh
    ("2.001682", "1.001612"),

    # Nhóm 6: Xây dựng
    ("1.004850", "1.013225"),

    # Nhóm 7: An toàn thực phẩm / Lao động / Karaoke
    ("1.003820", "2.001827"),
    ("1.005000", "1.014748"),
    ("1.005100", "1.001029"),
    ("1.005300", "1.014199"),
]

# Các mã giữ nguyên nhưng cần cập nhật source_url
KEEP_CODES = [
    "1.001057", "1.001123", "1.001125", "1.003311",
    "1.003453", "1.003454", "1.003670", "1.004700",
    "1.005200", "2.002400",
]


def run():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    updated = 0

    for old_code, new_code in UPDATES:
        cur.execute(
            "UPDATE procedures SET code = %s, source_url = %s, updated_at = NOW() WHERE code = %s",
            (new_code, DVC_BASE + new_code, old_code)
        )
        n = cur.rowcount
        if n > 0:
            print(f"  ✓ {old_code:14} → {new_code}")
            updated += n
        else:
            print(f"  ✗ {old_code:14} NOT FOUND in database")

    # Cập nhật source_url cho các mã giữ nguyên
    for code in KEEP_CODES:
        cur.execute(
            "UPDATE procedures SET source_url = %s, updated_at = NOW() WHERE code = %s",
            (DVC_BASE + code, code)
        )
        if cur.rowcount > 0:
            print(f"  ~ {code:14} URL updated (code kept)")

    conn.commit()
    print(f"\nHoàn tất: {updated} mã thủ tục đã được cập nhật trong database.")
    conn.close()


if __name__ == "__main__":
    run()
