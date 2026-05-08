# Danh sách Thư viện và Giấy phép Phụ thuộc (Dependencies)

Dự án này sử dụng các thư viện và gói phần mềm nguồn mở. Dưới đây là danh sách phân loại chi tiết kèm theo giấy phép của chúng, đảm bảo tính minh bạch theo tiêu chí Phần Mềm Nguồn Mở.

## 1. Backend (Node.js)
| Tên Thư viện | Phiên bản | Giấy phép (License) | Mục đích sử dụng |
| --- | --- | --- | --- |
| express | 4.x | MIT | Web server framework |
| cors | 2.x | MIT | Xử lý Cross-Origin Resource Sharing |
| dotenv | 16.x | MIT | Quản lý biến môi trường |
| pg | 8.x | MIT | PostgreSQL client |

## 2. AI Service (Python)
| Tên Thư viện | Phiên bản | Giấy phép (License) | Mục đích sử dụng |
| --- | --- | --- | --- |
| fastapi | ^0.100 | MIT | API Framework |
| uvicorn | ^0.23 | BSD-3-Clause | ASGI Server |
| chromadb | 0.4.x | Apache 2.0 | Cơ sở dữ liệu Vector (AI/RAG) |
| langchain | 0.x | MIT | Quản lý logic AI và RAG model |

## 3. Frontend (React/Vite)
| Tên Thư viện | Phiên bản | Giấy phép (License) | Mục đích sử dụng |
| --- | --- | --- | --- |
| react | 18.x | MIT | UI Library |
| vite | 4.x | MIT | Trình đóng gói và môi trường phát triển |
| tailwindcss | 3.x | MIT | CSS Framework |

*Ghi chú: Tất cả các thư viện trên hoàn toàn tương thích với Giấy phép MIT của dự án. Không có thư viện nào bị thay đổi mã nguồn gốc (thỏa mãn tiêu chí OLP 2025).*