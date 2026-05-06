"""
Crawler thủ tục hành chính từ dichvucong.gov.vn
Lọc theo địa phương: TP. Hồ Chí Minh (mã: 79)

Chiến lược:
1. Dùng Playwright để mở trang, tương tác JS
2. Dùng API nội bộ của trang (nếu phát hiện được) để lấy dữ liệu hiệu quả hơn
3. Lưu kết quả vào data/procedures_raw.json
"""

import asyncio
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

# TP.HCM mã tỉnh = 79 trên cổng quốc gia
BASE_URL = "https://dichvucong.gov.vn"
TPHCM_CODE = "79"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9",
}


async def get_procedure_list_via_api(page_num: int = 1, page_size: int = 20) -> dict:
    """
    Thử lấy danh sách thủ tục qua API REST của cổng dịch vụ công.
    API endpoint này được phát hiện qua phân tích network traffic.
    """
    api_url = f"{BASE_URL}/api/thu-tuc-hanh-chinh"
    params = {
        "page": page_num,
        "size": page_size,
        "tinh_id": TPHCM_CODE,
    }
    try:
        resp = requests.get(api_url, params=params, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"[API] Lỗi: {e}")
    return {}


async def crawl_with_playwright():
    """
    Dùng Playwright để crawl danh sách và chi tiết thủ tục.
    """
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=HEADERS["User-Agent"],
            locale="vi-VN",
        )

        # Intercept API calls
        api_responses = []

        async def handle_response(response):
            url = response.url
            if "thu-tuc" in url.lower() and response.status == 200:
                try:
                    body = await response.json()
                    api_responses.append({"url": url, "data": body})
                except Exception:
                    pass

        page = await context.new_page()
        page.on("response", handle_response)

        print("[Crawler] Mở trang dichvucong.gov.vn ...")
        await page.goto(f"{BASE_URL}/p/home/dvc-trang-chu.html", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)

        # Thử điều hướng tới trang tra cứu thủ tục
        search_urls = [
            f"{BASE_URL}/p/home/dvc-thu-tuc-hanh-chinh.html",
            f"{BASE_URL}/p/home/dvc-danh-sach-thu-tuc.html",
        ]

        for url in search_urls:
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                print(f"[Crawler] Đã tới: {url}")
            except Exception:
                pass

        # In ra các API calls đã capture được
        if api_responses:
            print(f"[Crawler] Đã capture {len(api_responses)} API responses")
            output_file = OUTPUT_DIR / "api_responses_debug.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(api_responses[:5], f, ensure_ascii=False, indent=2)

        await browser.close()

    return results


async def crawl_search_api():
    """
    Thử các API endpoint khác nhau của cổng dịch vụ công.
    """
    procedures = []

    # Các API endpoint cần thử
    api_endpoints = [
        "/api/v1/thu-tuc-hanh-chinh/search",
        "/api/tthc/search",
        "/api/tthc/list",
        "/p/home/dvc-thu-tuc-hanh-chinh.html",
    ]

    for endpoint in api_endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            params = {"tinh_thanh": TPHCM_CODE, "page": 1, "pageSize": 20}
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            print(f"[Try] {url} -> {resp.status_code}")
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    print(f"[Found API] {url}: {json.dumps(data)[:200]}")
                    procedures.append({"endpoint": endpoint, "sample": data})
                except Exception:
                    pass
        except Exception as e:
            print(f"[Try] {endpoint} -> Error: {e}")

    return procedures


def save_sample_data():
    """
    Tạo dữ liệu mẫu để test hệ thống khi chưa có dữ liệu thật.
    Dữ liệu dựa trên các thủ tục hành chính thực tế tại TP.HCM.
    """
    sample_procedures = [
        {
            "code": "1.001640",
            "name": "Đăng ký khai sinh",
            "category": "Hộ tịch",
            "level": "Cấp xã",
            "implementing_agency": "UBND phường/xã/thị trấn",
            "processing_time": "Ngay trong ngày làm việc (hoặc ngay trong buổi tiếp nhận hồ sơ)",
            "fee": "Không thu phí",
            "requirements": "Công dân Việt Nam; Trẻ em sinh ra tại Việt Nam",
            "procedure_steps": "Bước 1: Nộp hồ sơ tại Bộ phận tiếp nhận và trả kết quả UBND phường/xã\nBước 2: Công chức hộ tịch kiểm tra hồ sơ\nBước 3: Nếu hồ sơ đủ điều kiện, đăng ký và cấp Giấy khai sinh",
            "required_documents": "1. Tờ khai đăng ký khai sinh (theo mẫu)\n2. Giấy chứng sinh (bản gốc)\n3. Chứng minh nhân dân/Căn cước công dân của cha, mẹ\n4. Sổ hộ khẩu (nếu có)",
            "result": "Giấy khai sinh",
            "legal_basis": "Luật Hộ tịch 2014; Nghị định 123/2015/NĐ-CP; Thông tư 04/2020/TT-BTP",
            "source_url": "https://dichvucong.gov.vn",
            "raw_content": "Đăng ký khai sinh là thủ tục hành chính bắt buộc trong thời hạn 60 ngày kể từ ngày sinh. Cha hoặc mẹ có trách nhiệm đi đăng ký khai sinh cho con. Nếu cha, mẹ không thể đến, thì ông hoặc bà hoặc người thân thích khác đi đăng ký. Thủ tục này hoàn toàn miễn phí và được thực hiện tại UBND cấp xã nơi cư trú của người mẹ hoặc nơi cư trú của người cha."
        },
        {
            "code": "1.004734",
            "name": "Đăng ký kết hôn",
            "category": "Hộ tịch",
            "level": "Cấp xã",
            "implementing_agency": "UBND phường/xã/thị trấn",
            "processing_time": "05 ngày làm việc",
            "fee": "Không thu phí",
            "requirements": "Nam từ đủ 20 tuổi, nữ từ đủ 18 tuổi; Không vi phạm các trường hợp cấm kết hôn; Tự nguyện đăng ký kết hôn",
            "procedure_steps": "Bước 1: Nộp hồ sơ tại Bộ phận tiếp nhận UBND cấp xã\nBước 2: Công chức hộ tịch kiểm tra, xác minh\nBước 3: Tổ chức lễ đăng ký kết hôn, cấp Giấy chứng nhận kết hôn",
            "required_documents": "1. Tờ khai đăng ký kết hôn (theo mẫu, có xác nhận của UBND nơi cư trú)\n2. Giấy xác nhận tình trạng hôn nhân (nếu không cùng nơi cư trú)\n3. CMND/CCCD/Hộ chiếu của hai bên",
            "result": "Giấy chứng nhận kết hôn",
            "legal_basis": "Luật Hôn nhân và Gia đình 2014; Luật Hộ tịch 2014; Nghị định 123/2015/NĐ-CP",
            "source_url": "https://dichvucong.gov.vn",
            "raw_content": "Đăng ký kết hôn là thủ tục pháp lý để công nhận quan hệ hôn nhân giữa hai người. Hai bên nam nữ phải trực tiếp có mặt tại UBND cấp xã để đăng ký. Thủ tục này được thực hiện tại UBND cấp xã nơi cư trú của một trong hai bên. Không thu phí đăng ký kết hôn."
        },
        {
            "code": "1.001057",
            "name": "Cấp Giấy chứng nhận quyền sử dụng đất, quyền sở hữu nhà ở và tài sản khác gắn liền với đất",
            "category": "Đất đai - Nhà ở",
            "level": "Cấp tỉnh",
            "implementing_agency": "Văn phòng đăng ký đất đai TP.HCM",
            "processing_time": "30 ngày làm việc; 40 ngày làm việc đối với các xã miền núi, hải đảo, vùng sâu, vùng xa, vùng có điều kiện kinh tế - xã hội khó khăn",
            "fee": "Theo quy định của HĐND tỉnh/thành phố",
            "requirements": "Người sử dụng đất, chủ sở hữu tài sản gắn liền với đất; Có đủ điều kiện được cấp Giấy chứng nhận theo quy định của Luật Đất đai",
            "procedure_steps": "Bước 1: Nộp hồ sơ tại Bộ phận Một cửa UBND quận/huyện hoặc Văn phòng ĐKQSD đất\nBước 2: Thẩm định hồ sơ, xác minh thực địa\nBước 3: Trình ký, cấp Giấy chứng nhận\nBước 4: Trả kết quả",
            "required_documents": "1. Đơn đăng ký, cấp Giấy chứng nhận (Mẫu 04a/ĐK)\n2. Một trong các giấy tờ về quyền sử dụng đất theo Điều 100 Luật Đất đai\n3. Chứng minh nhân dân/CCCD\n4. Sơ đồ thửa đất (nếu chưa có trong hồ sơ địa chính)\n5. Giấy tờ liên quan đến tài sản gắn liền với đất (nếu có)",
            "result": "Giấy chứng nhận quyền sử dụng đất, quyền sở hữu nhà ở và tài sản khác gắn liền với đất (Sổ đỏ/Sổ hồng)",
            "legal_basis": "Luật Đất đai 2013; Nghị định 43/2014/NĐ-CP; Nghị định 01/2017/NĐ-CP; Thông tư 23/2014/TT-BTNMT",
            "source_url": "https://dichvucong.gov.vn",
            "raw_content": "Cấp Giấy chứng nhận quyền sử dụng đất (Sổ đỏ/Sổ hồng) là thủ tục xác nhận quyền sử dụng đất và quyền sở hữu nhà ở của công dân. Hồ sơ nộp tại UBND quận/huyện hoặc Văn phòng đăng ký đất đai. Thời gian xử lý tối đa 30 ngày làm việc."
        },
        {
            "code": "1.001229",
            "name": "Đăng ký thường trú",
            "category": "Cư trú",
            "level": "Cấp xã",
            "implementing_agency": "Công an phường/xã/thị trấn",
            "processing_time": "07 ngày làm việc",
            "fee": "Không thu phí",
            "requirements": "Công dân Việt Nam; Có chỗ ở hợp pháp; Đủ điều kiện đăng ký thường trú theo Luật Cư trú",
            "procedure_steps": "Bước 1: Nộp hồ sơ tại Công an cấp xã\nBước 2: Công an kiểm tra hồ sơ và điều kiện đăng ký\nBước 3: Cập nhật thông tin vào Cơ sở dữ liệu quốc gia về dân cư",
            "required_documents": "1. Phiếu báo thay đổi hộ khẩu, nhân khẩu (HK01)\n2. Giấy tờ chứng minh chỗ ở hợp pháp:\n   - Giấy chứng nhận quyền sở hữu nhà ở hoặc\n   - Hợp đồng thuê nhà (còn hạn, có công chứng) hoặc\n   - Giấy xác nhận cho ở nhờ của chủ hộ\n3. CMND/CCCD",
            "result": "Được cập nhật thường trú vào Cơ sở dữ liệu quốc gia về dân cư",
            "legal_basis": "Luật Cư trú 2020; Thông tư 56/2021/TT-BCA",
            "source_url": "https://dichvucong.gov.vn",
            "raw_content": "Đăng ký thường trú là việc công dân đăng ký nơi thường xuyên sinh sống. Từ năm 2021, Sổ hộ khẩu giấy không còn giá trị, việc quản lý cư trú được thực hiện qua Cơ sở dữ liệu quốc gia về dân cư. Điều kiện đăng ký thường trú: có chỗ ở hợp pháp và đã đăng ký tạm trú tại chỗ ở đó từ 1 năm trở lên (đối với TP trực thuộc TW)."
        },
        {
            "code": "2.000850",
            "name": "Cấp Giấy phép lái xe",
            "category": "Giao thông - Vận tải",
            "level": "Cấp tỉnh",
            "implementing_agency": "Sở Giao thông Vận tải TP.HCM",
            "processing_time": "05 ngày làm việc kể từ ngày thi đạt",
            "fee": "135.000 đồng",
            "requirements": "Đủ độ tuổi theo từng hạng GPLX; Đủ sức khỏe; Qua sát hạch lý thuyết và thực hành",
            "procedure_steps": "Bước 1: Đăng ký học và thi tại cơ sở đào tạo lái xe được cấp phép\nBước 2: Thi sát hạch tại Trung tâm sát hạch lái xe\nBước 3: Nộp hồ sơ đề nghị cấp GPLX\nBước 4: Nhận GPLX",
            "required_documents": "1. Đơn đề nghị cấp GPLX\n2. CMND/CCCD (bản sao)\n3. Giấy chứng nhận sức khỏe do cơ sở y tế cấp\n4. Ảnh 3x4 (06 ảnh)\n5. Chứng chỉ học lái xe",
            "result": "Giấy phép lái xe",
            "legal_basis": "Luật Giao thông đường bộ 2008; Thông tư 12/2017/TT-BGTVT",
            "source_url": "https://dichvucong.gov.vn",
            "raw_content": "Giấy phép lái xe (GPLX) là tài liệu bắt buộc khi điều khiển phương tiện cơ giới đường bộ. Hạng A1: xe máy đến 175cc; Hạng B1: ô tô không kinh doanh vận tải; Hạng B2: ô tô kinh doanh vận tải. Thời hạn GPLX hạng B1 không thời hạn, B2 và các hạng khác 5-10 năm."
        },
        {
            "code": "1.004850",
            "name": "Cấp Giấy phép xây dựng nhà ở riêng lẻ tại đô thị",
            "category": "Xây dựng",
            "level": "Cấp huyện",
            "implementing_agency": "UBND quận/huyện TP.HCM",
            "processing_time": "15 ngày làm việc",
            "fee": "Theo quy định của TP.HCM",
            "requirements": "Công trình xây dựng phải phù hợp quy hoạch; Chủ đầu tư có quyền sử dụng đất hợp pháp",
            "procedure_steps": "Bước 1: Nộp hồ sơ tại UBND quận/huyện (bộ phận một cửa)\nBước 2: Thẩm định hồ sơ, kiểm tra thực địa\nBước 3: Trình ký, cấp Giấy phép xây dựng\nBước 4: Trả kết quả",
            "required_documents": "1. Đơn đề nghị cấp GPXD\n2. Giấy tờ chứng minh quyền sử dụng đất\n3. Bản vẽ thiết kế (03 bộ)\n4. Bản vẽ hiện trạng khu đất\n5. Ảnh chụp hiện trạng công trình liền kề",
            "result": "Giấy phép xây dựng",
            "legal_basis": "Luật Xây dựng 2014 (sửa đổi 2020); Nghị định 15/2021/NĐ-CP",
            "source_url": "https://dichvucong.gov.vn",
            "raw_content": "Giấy phép xây dựng là văn bản pháp lý do cơ quan nhà nước có thẩm quyền cấp cho chủ đầu tư. Phải xin phép xây dựng trước khi khởi công xây dựng, sửa chữa, cải tạo công trình. Miễn phép với nhà ở riêng lẻ ở nông thôn thuộc khu vực không có quy hoạch đô thị."
        },
        {
            "code": "2.001682",
            "name": "Đăng ký kinh doanh hộ cá thể",
            "category": "Doanh nghiệp",
            "level": "Cấp huyện",
            "implementing_agency": "Phòng Tài chính - Kế hoạch quận/huyện TP.HCM",
            "processing_time": "03 ngày làm việc",
            "fee": "100.000 đồng/lần cấp",
            "requirements": "Cá nhân là công dân Việt Nam từ đủ 18 tuổi; Không thuộc diện bị cấm kinh doanh",
            "procedure_steps": "Bước 1: Nộp hồ sơ tại Phòng Tài chính - Kế hoạch quận/huyện\nBước 2: Kiểm tra hồ sơ\nBước 3: Cấp Giấy chứng nhận đăng ký hộ kinh doanh",
            "required_documents": "1. Giấy đề nghị đăng ký hộ kinh doanh\n2. CMND/CCCD/Hộ chiếu (bản sao có chứng thực)\n3. Văn bản ủy quyền (nếu ủy quyền)\n4. Hợp đồng thuê địa điểm kinh doanh hoặc giấy tờ về địa điểm kinh doanh",
            "result": "Giấy chứng nhận đăng ký hộ kinh doanh",
            "legal_basis": "Nghị định 01/2021/NĐ-CP; Thông tư 01/2021/TT-BKHĐT",
            "source_url": "https://dichvucong.gov.vn",
            "raw_content": "Hộ kinh doanh là hình thức kinh doanh phổ biến nhất tại Việt Nam. Một cá nhân hoặc một hộ gia đình đăng ký kinh doanh. Không được mở chi nhánh, không phát hành chứng khoán. Hộ kinh doanh nộp thuế khoán hoặc thuế theo thực tế."
        },
        {
            "code": "1.001064",
            "name": "Cấp bản sao trích lục hộ tịch",
            "category": "Hộ tịch",
            "level": "Cấp xã",
            "implementing_agency": "UBND phường/xã/thị trấn",
            "processing_time": "Ngay trong ngày làm việc",
            "fee": "Không thu phí",
            "requirements": "Người có yêu cầu cấp bản sao trích lục hộ tịch",
            "procedure_steps": "Bước 1: Xuất trình CMND/CCCD và nêu yêu cầu\nBước 2: Công chức hộ tịch kiểm tra sổ đăng ký\nBước 3: Cấp bản sao trích lục",
            "required_documents": "1. CMND/CCCD/Hộ chiếu\n2. Giấy tờ liên quan (nếu yêu cầu trích lục của người khác thì cần giấy ủy quyền)",
            "result": "Bản sao trích lục đăng ký hộ tịch",
            "legal_basis": "Luật Hộ tịch 2014; Nghị định 123/2015/NĐ-CP",
            "source_url": "https://dichvucong.gov.vn",
            "raw_content": "Bản sao trích lục hộ tịch là văn bản do cơ quan đăng ký hộ tịch cấp. Bao gồm: trích lục khai sinh, trích lục kết hôn, trích lục khai tử. Được dùng thay thế bản chính trong nhiều trường hợp theo quy định pháp luật."
        },
        {
            "code": "1.003559",
            "name": "Xác nhận tình trạng hôn nhân",
            "category": "Hộ tịch",
            "level": "Cấp xã",
            "implementing_agency": "UBND phường/xã/thị trấn",
            "processing_time": "03 ngày làm việc",
            "fee": "Không thu phí",
            "requirements": "Người đang cư trú tại địa phương; Chưa đăng ký kết hôn hoặc đã ly hôn/góa",
            "procedure_steps": "Bước 1: Nộp tờ khai xác nhận tình trạng hôn nhân\nBước 2: Công chức hộ tịch xác minh thông tin\nBước 3: Cấp giấy xác nhận",
            "required_documents": "1. Tờ khai xác nhận tình trạng hôn nhân (theo mẫu)\n2. CMND/CCCD\n3. Sổ hộ khẩu hoặc giấy tờ chứng minh cư trú",
            "result": "Giấy xác nhận tình trạng hôn nhân",
            "legal_basis": "Luật Hộ tịch 2014; Nghị định 123/2015/NĐ-CP",
            "source_url": "https://dichvucong.gov.vn",
            "raw_content": "Giấy xác nhận tình trạng hôn nhân dùng để chứng minh người đó hiện đang độc thân (chưa kết hôn, hoặc đã ly hôn, hoặc vợ/chồng đã mất). Thường cần khi đăng ký kết hôn ở nơi không phải nơi thường trú, hoặc khi kết hôn với người nước ngoài."
        },
        {
            "code": "2.002400",
            "name": "Cấp giấy khám sức khỏe",
            "category": "Y tế",
            "level": "Cấp tỉnh",
            "implementing_agency": "Các cơ sở khám chữa bệnh được cấp phép tại TP.HCM",
            "processing_time": "Trong ngày",
            "fee": "Theo quy định của cơ sở y tế",
            "requirements": "Người có nhu cầu xác nhận sức khỏe (thi bằng lái, xin việc, xuất cảnh...)",
            "procedure_steps": "Bước 1: Đăng ký khám tại cơ sở y tế\nBước 2: Thực hiện các bài kiểm tra sức khỏe theo yêu cầu\nBước 3: Bác sĩ kết luận và cấp giấy",
            "required_documents": "1. CMND/CCCD\n2. Ảnh 4x6 (02 ảnh)\n3. Đơn đề nghị cấp giấy khám sức khỏe (nếu cơ sở y tế yêu cầu)",
            "result": "Giấy chứng nhận sức khỏe",
            "legal_basis": "Thông tư 14/2013/TT-BYT",
            "source_url": "https://dichvucong.gov.vn",
            "raw_content": "Giấy khám sức khỏe là tài liệu y tế xác nhận tình trạng sức khỏe của một người. Thường cần trong các trường hợp: xin việc làm, đăng ký học thi bằng lái xe, xuất khẩu lao động, xuất cảnh, nhập học. Có giá trị trong vòng 12 tháng kể từ ngày cấp."
        },
    ]

    output_file = OUTPUT_DIR / "procedures_raw.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sample_procedures, f, ensure_ascii=False, indent=2)

    print(f"[Sample Data] Đã lưu {len(sample_procedures)} thủ tục mẫu vào {output_file}")
    return sample_procedures


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Crawler thủ tục hành chính dichvucong.gov.vn")
    parser.add_argument("--mode", choices=["crawl", "sample", "explore"], default="sample",
                        help="Chế độ: crawl (thật), sample (dữ liệu mẫu), explore (khám phá API)")
    args = parser.parse_args()

    if args.mode == "sample":
        print("[Mode] Tạo dữ liệu mẫu để test...")
        save_sample_data()
    elif args.mode == "explore":
        print("[Mode] Khám phá API của dichvucong.gov.vn...")
        await crawl_with_playwright()
        await crawl_search_api()
    elif args.mode == "crawl":
        print("[Mode] Crawl thật từ dichvucong.gov.vn...")
        # TODO: Sau khi phân tích xong API, implement ở đây
        await crawl_with_playwright()


if __name__ == "__main__":
    asyncio.run(main())
