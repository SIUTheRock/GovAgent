"""
Sửa lại mã thủ tục (code) trong procedures_raw.json dựa trên đối chiếu
với hệ thống DVC (dichvucong.gov.vn) qua FTS search và dvc_code_mapping.json.

Có 20 trong 30 mã cần sửa:
- 4 mã có hậu tố A/B (không đúng định dạng DVC)
- 16 mã khác đối chiếu từ DVC FTS với độ tin cậy cao
"""

import json
from pathlib import Path

DATA_FILE = Path("data/procedures_raw.json")
DVC_BASE_URL = "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc="

# Bảng sửa mã thủ tục: {mã_cũ: (mã_mới, lý_do)}
CODE_FIXES = {
    # =========================================================
    # Nhóm 1: Mã có hậu tố A/B (sai định dạng DVC, bắt buộc sửa)
    # =========================================================
    "1.004850A": ("1.013226",
        "Mã không chuẩn DVC. Điều chỉnh GPXD mới đối với công trình cấp III, IV → 1.013226"),
    "2.000850A": ("3.000347",
        "Mã không chuẩn DVC. Đổi giấy phép lái xe → 3.000347 (DVC FTS score=3, exact match)"),
    "2.000850B": ("3.000348",
        "Mã không chuẩn DVC. Cấp lại giấy phép lái xe → 3.000348 (DVC FTS all_results)"),
    "2.001682A": ("2.000720",
        "Mã không chuẩn DVC. Thay đổi nội dung đăng ký hộ kinh doanh → 2.000720 (DVC FTS score=3)"),

    # =========================================================
    # Nhóm 2: Hộ tịch - đối chiếu DVC FTS score=3 (độ tin cậy cao)
    # =========================================================
    "1.001640": ("1.001193",
        "Đăng ký khai sinh. DVC FTS: 1.001193 'Thủ tục đăng ký khai sinh' (score=3)"),
    "1.004734": ("1.000894",
        "Đăng ký kết hôn. DVC FTS: 1.000894 'Thủ tục đăng ký kết hôn' (score=3)"),
    "1.004792": ("1.000656",
        "Đăng ký khai tử. DVC FTS: 1.000656 'Thủ tục đăng ký khai tử' (score=3)"),
    "1.004800": ("1.004884",
        "Đăng ký lại khai sinh. DVC FTS: 1.004884 'Thủ tục đăng ký lại khai sinh' (score=3)"),
    "1.001064": ("2.000635",
        "Cấp bản sao trích lục hộ tịch. DVC FTS: 2.000635 'Cấp bản sao Trích lục hộ tịch' (score=3)"),
    "1.003559": ("1.004873",
        "Xác nhận tình trạng hôn nhân. DVC FTS: 1.004873 'Thủ tục cấp Giấy xác nhận tình trạng hôn nhân' (score=3)"),
    "1.004621": ("1.000881",
        "Đăng ký thay đổi, cải chính hộ tịch. DVC FTS all_results: 1.000881 'Thủ tục đăng ký việc thay đổi, cải chính, bổ sung hộ tịch'"),

    # =========================================================
    # Nhóm 3: Cư trú - đối chiếu DVC FTS score=3
    # =========================================================
    "1.001229": ("1.004222",
        "Đăng ký thường trú. DVC FTS: 1.004222 'Đăng ký thường trú' (score=3, exact match)"),
    "1.003306": ("1.004194",
        "Đăng ký tạm trú. DVC FTS: 1.004194 'Đăng ký tạm trú' (score=3, exact match)"),

    # =========================================================
    # Nhóm 4: Giao thông - Giấy phép lái xe
    # =========================================================
    "2.000850": ("3.000346",
        "Cấp giấy phép lái xe. DVC FTS all_results: 3.000346 'Cấp giấy phép lái xe' (exact match)"),

    # =========================================================
    # Nhóm 5: Kinh doanh / Doanh nghiệp
    # =========================================================
    "2.001682": ("1.001612",
        "Đăng ký kinh doanh hộ cá thể. DVC FTS: 1.001612 'Đăng ký thành lập hộ kinh doanh' (best match)"),

    # =========================================================
    # Nhóm 6: Xây dựng
    # =========================================================
    "1.004850": ("1.013225",
        "Cấp GPXD nhà ở riêng lẻ đô thị. DVC FTS all_results: 1.013225 'Cấp GPXD mới đối với công trình cấp III, cấp IV'"),

    # =========================================================
    # Nhóm 7: An toàn thực phẩm, Lao động, Karaoke
    # =========================================================
    "1.003820": ("2.001827",
        "Cấp GCN cơ sở đủ điều kiện ATTP. DVC FTS: 2.001827 'Cấp GCN cơ sở đủ ĐK ATTP đối với cơ sở SX, KD thực phẩm NLT' (score=3)"),
    "1.005000": ("1.014748",
        "Hưởng trợ cấp thất nghiệp. DVC FTS: 1.014748 'Hưởng trợ cấp thất nghiệp (Cấp tỉnh)' (score=3)"),
    "1.005100": ("1.001029",
        "Cấp giấy phép kinh doanh dịch vụ karaoke. DVC FTS: 1.001029 'Thủ tục cấp giấy phép đủ điều kiện kinh doanh dịch vụ karaoke'"),
    "1.005300": ("1.014199",
        "Cấp giấy phép lao động người nước ngoài. DVC FTS all_results: 1.014199 'Cấp giấy phép lao động đối với người lao động nước ngoài làm việc tại VN'"),
}

# Mã giữ nguyên (không đủ bằng chứng để thay đổi)
KEEP_CODES = {
    "1.001057": "Cấp GCN QSD đất - không tìm được mã chính xác hơn",
    "1.001123": "Chuyển mục đích SD đất - không tìm được mã chính xác hơn",
    "1.001125": "Đăng ký sang tên QSD đất - không tìm được mã chính xác hơn",
    "1.003311": "Tách hộ khẩu - thủ tục có thể đã hết hiệu lực (Luật Cư trú 2020)",
    "1.003453": "Cấp phiếu LLTP số 1 - không đủ độ tin cậy để thay đổi",
    "1.003454": "Cấp phiếu LLTP số 2 - không đủ độ tin cậy để thay đổi",
    "1.003670": "Đăng ký nhận nuôi con nuôi trong nước - không tìm được mã chính xác hơn",
    "1.004700": "Xác nhận hộ nghèo, hộ cận nghèo - không tìm được mã chính xác hơn",
    "1.005200": "Đăng ký bảo hộ nhãn hiệu hàng hóa - không tìm được mã chính xác hơn",
    "2.002400": "Cấp giấy khám sức khỏe - không tìm được mã trên DVC",
}


def fix_codes():
    with open(DATA_FILE, encoding="utf-8") as f:
        procedures = json.load(f)

    changed = 0
    for p in procedures:
        old_code = p["code"]
        if old_code in CODE_FIXES:
            new_code, reason = CODE_FIXES[old_code]
            print(f"  SỬAA: {old_code} → {new_code}")
            print(f"         [{p['name'][:50]}]")
            print(f"         Lý do: {reason[:80]}")
            p["code"] = new_code
            # Cập nhật source_url thành URL thực tế trên DVC
            p["source_url"] = DVC_BASE_URL + new_code
            changed += 1
        elif old_code in KEEP_CODES:
            # Cập nhật source_url ngay cả khi giữ code cũ
            p["source_url"] = DVC_BASE_URL + old_code
            print(f"  GIỮ:  {old_code} | {p['name'][:50]}")
        else:
            print(f"  ???:  {old_code} | {p['name'][:50]} (không có trong danh sách)")

    print(f"\nTổng: {changed}/{len(procedures)} mã đã được sửa")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(procedures, f, ensure_ascii=False, indent=2)
    print(f"Đã ghi lại: {DATA_FILE}")


if __name__ == "__main__":
    fix_codes()
