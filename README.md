# PPNCKH - Hệ thống Tra cứu Dịch vụ công bằng AI và Dữ liệu Mở (OLP 2025)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-green.svg)](CHANGELOG.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

Đây là dự án phát triển Hệ thống Trợ lý ảo AI & Tra cứu Dịch vụ công (DVC) được thiết kế đặc biệt đáp ứng **Chủ đề Phần mềm nguồn mở Olympic Tin học 2025: "Ứng dụng dữ liệu mở liên kết phục vụ chuyển đổi số"**. 

Dự án giải quyết bài toán thực thực tế: **Minh bạch hóa và hỗ trợ người dân tự động hóa việc hỏi đáp thủ tục hành chính, đồng thời tích hợp chặt chẽ việc truy xuất dữ liệu theo chuẩn Semantic Web và vạn vật kết nối (IoT).**

## 🌟 Tính Năng Nổi Bật & Chuẩn Công Nghệ

1. **Trợ lý Ảo AI (RAG System)** 
   Sử dụng RAG (Retrieval-Augmented Generation) kết hợp ChromaDB và Gemini/LLM để tư vấn rành mạch các bước làm hồ sơ cho người dân.
2. **Mạng Dữ liệu Mở Liên kết (LOD)** 
   Dữ liệu được làm giàu (crawl trực tiếp từ Cổng DVC Quốc gia) và xuất khẩu công khai dưới định dạng **JSON-LD** (`schema.org/PublicService`). Không chỉ hiển thị, hệ thống cho phép các tổ chức thứ ba liên kết lấy siêu dữ liệu.
3. **FIWARE NGSI-LD & Smart City**
   Bảo đảm đáp ứng xu hướng Đô thị thông minh (Smart City). Tích hợp endpoint REST xuất danh mục dưới chuẩn NGSI-LD (ETSI).
4. **Ontology SOSA/SSN cho IoT**
   Giải quyết trọn vẹn yêu cầu công nghệ IoT mở rộng. Từng Cơ quan hành chính đều gắn tọa độ địa lý dựa trên OpenStreetMap và liên kết thời gian thực với dữ liệu thời tiết (Sensors) thông qua cấu trúc Ontology SOSA/SSN.

## 🏗 Kiến Trúc & Cấu Trúc Dự Án (Microservices)

```plaintext
PPNCKH/
├── frontend/          # React 18 + TailwindCSS + React Router (Giao diện người dùng cuối & Nút Export LOD)
├── backend/           # Node.js + Express.js REST API (Xử lý Context NGSI-LD/SOSA & Map Data DB)
├── ai-service/        # Python FastAPI + LangChain ChromaDB (Service RAG)
├── crawler/           # Pipeline Auto-Crawl DVC Quốc Gia (Thành phần Crawler Data pipeline)
├── database/          # PostgreSQL schema và Init files
├── docker-compose.yml # Containerization chuẩn hóa
└── Makefile           # Script biên dịch tự động
```

## 🚀 Cài Đặt và Khởi Động Nhanh (Dành cho Giám khảo)

Dự án được tối ưu để chỉ mất dưới 3 phút thiết lập. Môi trường độc lập hoàn toàn không yêu cầu cấu hình thủ công rối rắm.

### Yêu cầu
- Node.js 20+
- Python 3.12+ (Hoặc Conda Environment)
- PostgreSQL 16
- *(Khuyến nghị)* Docker & Docker Compose

### Cài đặt tự động một chạm (Khuyên dùng)
Cấu trúc `Makefile` sẽ tự động phân phối tệp biến môi trường `.env` và kích hoạt hệ thống:
```bash
# Cài đặt môi trường và các thư viện cần thiết
make setup

# Khởi chạy toàn bộ các dịch vụ Backend, Frontend, AI
make start
```

### Cài đặt thủ công qua Script (Trên Windows)
Nếu bạn chấm thi trên hệ điều hành Windows:
```powershell
# Chạy file để cài đặt tự động dependencies bằng PowerShell
.\start-dev.ps1
```

## 🔌 Tích Hợp API Chức Năng Cốt Lõi
| Method | Endpoint | Giá trị khai thác (Open Data) |
|--------|----------|-------|
| GET | `/api/procedures/:id?format=ngsi-ld` | Trả về dữ liệu chuẩn JSON-LD / NGSI-LD kèm IoT SOSA Observation. |
| GET | `/api/search` | Khai thác API Search Full-text thủ tục. |
| POST | `/api/chat` | Trao đổi Socket/REST với AI Bot. |

## 📖 Tài Liệu Quản Lý
Để đảm bảo tính bền vững của dự án rẽ nhánh sau cuộc thi, mời xem chi tiết tại:
- [Lịch sử Phiên bản (CHANGELOG.md)](CHANGELOG.md)
- [Báo cáo Lỗi & Tracker (Issues)](https://github.com/EdgarhLe/OLM/issues) - Nơi theo dõi vòng đời hệ thống.
- [Giấy phép (LICENSE)](LICENSE) - Cam kết ứng dụng tuân thủ chuẩn tự do nguồn mở OSI.
- [Quy tắc Đóng góp (CONTRIBUTING.md)](CONTRIBUTING.md)

## 🤝 Đóng Góp Nguồn Mở & Bản Quyền
Dự án nguồn mở hoàn toàn, được tái phân phối và cấp phép chỉnh sửa nâng cấp theo **Giấy phép MIT**. Xin vui lòng đọc kỹ `CONTRIBUTING.md` nếu bạn muốn cải thiện model AI hoặc liên kết thêm Open Data từ cơ sở hạ tầng của mình.