"""
Script thêm trường form_templates vào procedures_raw.json
Mỗi thủ tục sẽ có danh sách mẫu đơn kèm link tải chính thức.
"""
import json
from pathlib import Path

DATA_FILE = Path("data/procedures_raw.json")

# Mapping mã thủ tục -> danh sách mẫu đơn
FORM_TEMPLATES = {
    "1.001640": [  # Đăng ký khai sinh
        {
            "name": "Tờ khai đăng ký khai sinh",
            "code": "Mẫu TK01",
            "legal_ref": "Thông tư 04/2020/TT-BTP",
            "url": "https://moj.gov.vn/qt/tintuc/Pages/van-ban-phap-luat.aspx?ItemID=2855"
        }
    ],
    "1.004734": [  # Đăng ký kết hôn
        {
            "name": "Tờ khai đăng ký kết hôn",
            "code": "Mẫu TK02",
            "legal_ref": "Thông tư 04/2020/TT-BTP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.004734"
        }
    ],
    "1.001057": [  # Cấp GCN QSD đất (Sổ đỏ)
        {
            "name": "Đơn đăng ký, cấp Giấy chứng nhận",
            "code": "Mẫu 04a/ĐK",
            "legal_ref": "Thông tư 23/2014/TT-BTNMT",
            "url": "https://thuvienphapluat.vn/van-ban/Bat-dong-san/Thong-tu-23-2014-TT-BTNMT-Giay-chung-nhan-quyen-su-dung-dat-quyen-so-huu-nha-o-tai-san-238636.aspx"
        },
        {
            "name": "Đơn đăng ký biến động đất đai",
            "code": "Mẫu 09/ĐK",
            "legal_ref": "Thông tư 23/2014/TT-BTNMT",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001057"
        }
    ],
    "1.001229": [  # Đăng ký thường trú
        {
            "name": "Tờ khai thay đổi thông tin cư trú",
            "code": "Mẫu CT01",
            "legal_ref": "Thông tư 66/2023/TT-BCA",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001229"
        }
    ],
    "2.000850": [  # Cấp GPLX
        {
            "name": "Đơn đề nghị cấp giấy phép lái xe",
            "code": "Mẫu 02",
            "legal_ref": "Thông tư 12/2017/TT-BGTVT",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=2.000850"
        },
        {
            "name": "Giấy chứng nhận sức khỏe",
            "code": "Mẫu sức khỏe",
            "legal_ref": "Thông tư 14/2013/TT-BYT",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=2.000850"
        }
    ],
    "1.004850": [  # Cấp GPXD nhà ở riêng lẻ
        {
            "name": "Đơn đề nghị cấp giấy phép xây dựng",
            "code": "Mẫu số 01",
            "legal_ref": "Nghị định 15/2021/NĐ-CP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.004850"
        }
    ],
    "2.001682": [  # Đăng ký hộ kinh doanh
        {
            "name": "Giấy đề nghị đăng ký hộ kinh doanh",
            "code": "Phụ lục III-1",
            "legal_ref": "Nghị định 01/2021/NĐ-CP",
            "url": "https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Nghi-dinh-01-2021-ND-CP-dang-ky-doanh-nghiep-463560.aspx"
        }
    ],
    "1.001064": [  # Cấp bản sao trích lục hộ tịch
        {
            "name": "Giấy đề nghị cấp bản sao trích lục hộ tịch",
            "code": "Mẫu TK11",
            "legal_ref": "Thông tư 04/2020/TT-BTP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001064"
        }
    ],
    "1.003559": [  # Xác nhận tình trạng hôn nhân
        {
            "name": "Tờ khai xác nhận tình trạng hôn nhân",
            "code": "Mẫu TK14",
            "legal_ref": "Thông tư 04/2020/TT-BTP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.003559"
        }
    ],
    "2.002400": [  # Cấp giấy khám sức khỏe
        {
            "name": "Giấy chứng nhận sức khỏe",
            "code": "Mẫu sức khỏe",
            "legal_ref": "Thông tư 14/2013/TT-BYT",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=2.002400"
        }
    ],
    "1.004792": [  # Đăng ký khai tử
        {
            "name": "Tờ khai đăng ký khai tử",
            "code": "Mẫu TK03",
            "legal_ref": "Thông tư 04/2020/TT-BTP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.004792"
        }
    ],
    "1.003306": [  # Đăng ký tạm trú
        {
            "name": "Tờ khai thay đổi thông tin cư trú",
            "code": "Mẫu CT01",
            "legal_ref": "Thông tư 66/2023/TT-BCA",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.003306"
        }
    ],
    "1.003311": [  # Tách hộ khẩu
        {
            "name": "Tờ khai thay đổi thông tin cư trú",
            "code": "Mẫu CT01",
            "legal_ref": "Thông tư 66/2023/TT-BCA",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.003311"
        }
    ],
    "1.001123": [  # Chuyển mục đích sử dụng đất
        {
            "name": "Đơn xin phép chuyển mục đích sử dụng đất",
            "code": "Mẫu 01/ĐK",
            "legal_ref": "Thông tư 30/2014/TT-BTNMT",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001123"
        }
    ],
    "1.001125": [  # Sang tên QSD đất
        {
            "name": "Tờ khai đăng ký biến động đất đai",
            "code": "Mẫu 09/ĐK",
            "legal_ref": "Thông tư 23/2014/TT-BTNMT",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.001125"
        }
    ],
    "1.004850A": [  # Điều chỉnh GPXD
        {
            "name": "Đơn đề nghị điều chỉnh giấy phép xây dựng",
            "code": "Mẫu số 01 (điều chỉnh)",
            "legal_ref": "Nghị định 15/2021/NĐ-CP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.004850"
        }
    ],
    "2.001682A": [  # Thay đổi nội dung HKD
        {
            "name": "Thông báo thay đổi nội dung đăng ký hộ kinh doanh",
            "code": "Phụ lục III-2",
            "legal_ref": "Nghị định 01/2021/NĐ-CP",
            "url": "https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Nghi-dinh-01-2021-ND-CP-dang-ky-doanh-nghiep-463560.aspx"
        }
    ],
    "2.000850A": [  # Đổi GPLX
        {
            "name": "Đơn đề nghị đổi giấy phép lái xe",
            "code": "Mẫu 04",
            "legal_ref": "Thông tư 12/2017/TT-BGTVT",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=2.000850"
        }
    ],
    "2.000850B": [  # Cấp lại GPLX
        {
            "name": "Đơn đề nghị cấp lại giấy phép lái xe",
            "code": "Mẫu 05",
            "legal_ref": "Thông tư 12/2017/TT-BGTVT",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=2.000850"
        }
    ],
    "1.003453": [  # LLTP số 1
        {
            "name": "Tờ khai yêu cầu cấp Phiếu lý lịch tư pháp",
            "code": "Mẫu số 03/2013/TT-BTP",
            "legal_ref": "Thông tư 13/2011/TT-BTP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.003453"
        }
    ],
    "1.003454": [  # LLTP số 2
        {
            "name": "Tờ khai yêu cầu cấp Phiếu lý lịch tư pháp số 2",
            "code": "Mẫu số 03/2013/TT-BTP",
            "legal_ref": "Thông tư 13/2011/TT-BTP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.003454"
        }
    ],
    "1.003670": [  # Nuôi con nuôi
        {
            "name": "Tờ khai đăng ký nuôi con nuôi",
            "code": "Mẫu TP/CN-2013.NCN",
            "legal_ref": "Thông tư 12/2011/TT-BTP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.003670"
        }
    ],
    "1.004621": [  # Thay đổi cải chính HT
        {
            "name": "Tờ khai thay đổi, cải chính thông tin hộ tịch",
            "code": "Mẫu TK07",
            "legal_ref": "Thông tư 04/2020/TT-BTP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.004621"
        }
    ],
    "1.004800": [  # Đăng ký lại khai sinh
        {
            "name": "Tờ khai đăng ký lại khai sinh",
            "code": "Mẫu TK10",
            "legal_ref": "Thông tư 04/2020/TT-BTP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.004800"
        }
    ],
    "1.003820": [  # ATTP
        {
            "name": "Đơn đề nghị cấp Giấy chứng nhận ATTP",
            "code": "Mẫu số 01",
            "legal_ref": "Nghị định 15/2018/NĐ-CP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.003820"
        }
    ],
    "1.005000": [  # Hưởng TCTN
        {
            "name": "Đề nghị hưởng trợ cấp thất nghiệp",
            "code": "Mẫu số 03",
            "legal_ref": "Thông tư 28/2015/TT-BLĐTBXH",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.005000"
        }
    ],
    "1.004700": [  # Xác nhận hộ nghèo
        {
            "name": "Đơn đề nghị xác nhận hộ nghèo/cận nghèo",
            "code": "Mẫu đơn",
            "legal_ref": "Nghị định 07/2021/NĐ-CP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.004700"
        }
    ],
    "1.005100": [  # Karaoke
        {
            "name": "Đơn đề nghị cấp phép kinh doanh karaoke",
            "code": "Mẫu đơn",
            "legal_ref": "Nghị định 54/2019/NĐ-CP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.005100"
        }
    ],
    "1.005200": [  # Nhãn hiệu
        {
            "name": "Tờ khai đăng ký nhãn hiệu",
            "code": "Mẫu 04-NH",
            "legal_ref": "Thông tư 23/2019/TT-BKHCN",
            "url": "https://ipvietnam.gov.vn/web/guest/cac-to-khai-va-bieu-mau"
        }
    ],
    "1.005300": [  # GPLĐ nước ngoài
        {
            "name": "Đề nghị cấp giấy phép lao động",
            "code": "Mẫu số 11",
            "legal_ref": "Nghị định 152/2020/NĐ-CP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.005300"
        },
        {
            "name": "Lý lịch tự thuật (người lao động nước ngoài)",
            "code": "Mẫu số 16",
            "legal_ref": "Nghị định 152/2020/NĐ-CP",
            "url": "https://dichvucong.gov.vn/p/home/dvc-chi-tiet-thu-tuc-nganh-doc.html?ma_thu_tuc=1.005300"
        }
    ],
}


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        procedures = json.load(f)

    updated = 0
    for p in procedures:
        code = p.get("code", "")
        if code in FORM_TEMPLATES:
            p["form_templates"] = FORM_TEMPLATES[code]
            updated += 1
        else:
            p["form_templates"] = []

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(procedures, f, ensure_ascii=False, indent=2)

    print(f"[Done] Đã thêm form_templates cho {updated}/{len(procedures)} thủ tục.")


if __name__ == "__main__":
    main()
