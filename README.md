# PPNCKH - Hệ thống Tra cứu Dịch vụ công bằng AI và Dữ liệu Mở

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version: 1.0.0-alpha](https://img.shields.io/badge/Version-1.0.0--alpha-green.svg)](CHANGELOG.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

Đây là dự án phát triển Hệ thống Trợ lý ảo AI & Tra cứu Dịch vụ công (DVC) được thiết kế đặc biệt đáp ứng **Chủ đề OLP Phần mềm nguồn mở 2025: "Ứng dụng dữ liệu mở liên kết phục vụ chuyển đổi số"**.

## 🌟 Tính Năng Nổi Bật
1. **Trợ lý Ảo AI (RAG System):** Sử dụng RAG (Retrieval-Augmented Generation) kết hợp với ChromaDB để tư vấn hồ sơ, thủ tục chính xác cho người dân.
2. **Mạng Dữ liệu Mở Liên kết (LOD):** (*) Tích hợp chuẩn JSON-LD cung cấp Web semantic giúp các hệ thống bên ngoài khai thác và liên kết dữ liệu DVC.
3. **Tự động hóa Thu thập (Crawler):** Crawl và phân tích hàng ngàn thủ tục DVC một cách tự động, tập trung dữ liệu.
4. **Thiết kế Microservices:** Phân tách rõ ràng giữa Frontend, Backend và AI Service.

## 🏗 Cấu Trúc Dự Án
```plaintext
PPNCKH/
├── frontend/          # React 18 + TailwindCSS + React Router
├── backend/           # Node.js + Express.js REST API  
├── ai-service/        # Python FastAPI + LangChain RAG
├── crawler/           # Tập hợp các script Python thu thập và chuẩn hóa dữ liệu
├── database/          # PostgreSQL schema và Init files
├── data/              # Không gian lưu trữ dữ liệu ChromaDB, PostgreSQL...
└── docker-compose.yml 
```

## 🚀 Cài Đặt và Khởi Động Nhanh (Dành cho Giám khảo & Lập trình viên)

### Yêu cầu hệ thống
- Node.js 20+
- Python 3.12+
- PostgreSQL 16
- *(Tùy chọn)* Docker & Docker Compose

### Cài đặt tự động bằng Make (Khuyên dùng)
```bash
# Cài đặt môi trường và các thư viện cần thiết
make setup

# Khởi chạy toàn bộ các dịch vụ (Frontend, Backend, AI)
make start
```

### Cài đặt thủ công qua Script (Trên Windows)
Khởi chạy PowerShell và thực thi script:
```powershell
.\start-dev.ps1
```

## 🔌 API Endpoints
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/categories` | Danh sách lĩnh vực |
| GET | `/api/procedures` | Danh sách thủ tục |
| GET | `/api/search` | Tìm kiếm full-text |
| POST | `/api/chat` | Chat với AI `{ question, session_id }` |

## 📖 Tài Liệu Hướng Dẫn
- [Giấy phép (LICENSE)](LICENSE)
- [Danh sách Thư viện (DEPENDENCIES.md)](DEPENDENCIES.md)
- [Lịch sử Phiên bản (CHANGELOG.md)](CHANGELOG.md)
- [Quy tắc Đóng góp (CONTRIBUTING.md)](CONTRIBUTING.md)
- [Quy tắc Ứng xử (CODE_OF_CONDUCT.md)](CODE_OF_CONDUCT.md)

## 🤝 Đóng Góp Nguồn Mở
Vui lòng đọc kỹ `CONTRIBUTING.md` và `CODE_OF_CONDUCT.md` trước khi gửi Pull Request. Dự án được phân phối dưới giấy phép **MIT License**.
