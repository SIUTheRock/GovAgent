# PPNCKH - TỔNG HỢP KIẾN TRÚC MÃ NGUỒN VÀ DỰ ÁN

Tài liệu này tổng hợp toàn bộ thông tin cấu trúc, kiến trúc hệ thống, công nghệ (tech stack) và hướng dẫn chi tiết. Mục đích để AI (hoặc các nhà phát triển) có thể đọc, nắm bắt nhanh toàn bộ codebase hiện tại phục vụ việc phát triển, duy trì hay tái chạy dự án.

## 1. MỤC TIÊU DỰ ÁN
- **Tên dự án:** Hệ thống Trợ lý ảo AI & Tra cứu Dịch vụ công (PPNCKH).
- **Mục tiêu chính:** Tham gia kỳ thi OLP 2025 Phần mềm nguồn mở với chủ đề _"Ứng dụng dữ liệu mở liên kết phục vụ chuyển đổi số"_.
- **Tính năng cốt lõi:**
  - Tra cứu thủ tục hành chính áp dụng tại TP.HCM.
  - Trợ lý ảo AI (áp dụng RAG - Retrieval-Augmented Generation) tư vấn làm thủ tục hồ sơ.
  - Cơ sở hạ tầng dữ liệu theo tiêu chuẩn Semantic Web, LOD (Linked Open Data).
  - Tích hợp khái niệm Đô thị thông minh (Smart City) qua cơ chế FIWARE NGSI-LD & SOSA/SSN Ontology cho IoT.

## 2. KIẾN TRÚC HỆ THỐNG
Hệ thống sử dụng kiến trúc phân tán (Microservices) chia thành 4 thành phần thiết yếu:
1. **Frontend (Web App):** Giao diện người dùng sử dụng React kết nối với lõi qua REST API.
2. **Backend (Core API):** Quản lý Router, thông tin User cơ bản, giao tiếp trực tiếp CSDL PostgreSQL, đặc tả & chuẩn hóa dữ liệu NGSI-LD.
3. **AI Service:** Microservice bằng Python hoàn toàn chịu trách nhiệm xử lý text, tìm kiếm ngữ nghĩa ChromaDB và tạo sinh văn bản (LLM) trả lời theo dạng RAG.
4. **Data Crawler Pipeline:** Các bộ module tự cào & update dữ liệu tự động từ cổng DVC Quốc gia (`dichvucong.gov.vn`).

## 3. CÔNG NGHỆ ÁP DỤNG (TECH STACK)
- **Frontend:** Node.js, React 19, TailwindCSS 4, Vite, React-Router-DOM, React-Leaflet (tích hợp Map API).
- **Backend:** Node.js, Express.js 4.x, PostgreSQL adapter (`pg`), cors, helmet.
- **AI Service:** Python 3.12+, FastAPI, Uvicorn, LangChain, ChromaDB, Sentence-Transformers (tạo Embedding Text mượt), model LLM Gemini hoặc GPT.
- **Database:**
  - `PostgreSQL 16`: Database quản trị Relation (Danh mục, Thủ tục, Metadata, Agencies, Log Chat).
  - `ChromaDB`: Vector Database chuyên lưu trữ Text Embeddings cho truy vấn nội dung tương đồng (Semantic Search).
- **Crawler Scripts:** Công cụ Scrapy, Playwright hoặc requests/bs4 (gồm nhiều công cụ custom by-pass DVC).
- **DevOps:** Hỗ trợ cấu hình triệt để trên Docker & `docker-compose`.

## 4. CHI TIẾT CẤU TRÚC THƯ MỤC SOURCE CODE
```text
e:\PPNCKH\
├── ai-service/             # [Python] Máy chủ RAG và LLM chatbot
│   ├── main.py             # Entry point cho FastAPI (port 8001 / 8000)
│   ├── config.py           # Quản lý .env
│   ├── index_data.py       # Script nạp dữ liệu văn bản từ Postgres tạo vector vào ChromaDB
│   ├── rag/                # Thư mục nhân quy trình RAG (chain.py, embeddings.py, vectorstore.py)
│   ├── data/chroma_db/     # Lưu DB cục bộ của Chroma vector
│   └── requirements.txt    # Danh sách lib Python cho AI
├── backend/                # [Node.js] Lõi REST API chính
│   ├── src/app.js          # Entry point (port 5000)
│   ├── src/controllers/    # Xử lý logic API (categories, chat, admin, thủ tục...)
│   ├── src/db/             # Kết nối Database Postgres (postgres.js)
│   ├── src/routes/         # API Endpoint routers
│   └── package.json        
├── crawler/                # [Python] Bộ công cụ lấy dữ liệu (Web Scraping)
│   ├── crawler.py / process_data.py
│   ├── scripts/            # Hàng loạt các tools hack / find endpoint từ cổng DVC (call_dvc_fts.py, find_api_endpoint.py...)
│   └── data/               # Data gốc lưu trữ JSON, HTML nháp
├── database/               # [SQL] Setup Database
│   └── init.sql            # Scripts cấu trúc dữ liệu cho tables: categories, procedures, chat_logs, agencies...
├── frontend/               # [React] Trình diện Browser cho User
│   ├── index.html / main.jsx
│   ├── src/components/     # UI chia nhỏ: NavBar, ChatBox, Map...
│   ├── src/pages/          # Màn hình chính
│   └── package.json / vite.config.js 
├── docker-compose.yml      # Orchestration cho toàn app
├── README.md               # Readme giới thiệu public
└── Tong_hop_OLP_PMNM_2025.md # Hồ sơ năng lực đi thi ghi chú rõ tiêu chí OLP 2025
```

## 5. DATABASE SCHEMA (Lõi PostgreSQL)
Xem cấu trúc cụ thể trong file `database/init.sql`:
- **`categories`**: Nhóm thủ tục hành chính (ví dụ: Hộ tịch, Đất đai - Nhờ ở...).
- **`procedures`**: Chi tiết thủ tục (chứa `code`, `name`, `level`, `processing_time`, `procedure_steps`...). Cột `raw_content` dùng để query FTS (Full-Text Search Native Pg) hoặc RAG Chunking.
- **`agencies`**: Dữ liệu cơ quan giải quyết đi kèm tạo độ `lat, lng` tích hợp cho Web Map.
- **`chat_logs`**: Thu thập log để chấm điểm metrics đánh giá hiệu suất bot.

## 6. HƯỚNG DẪN CÀI ĐẶT & CHẠY LOCAL (DEVELOPMENT MODE CI/CD MIROSERVICES)

Nếu cần fix hay code thêm chạy local, triển khai theo thứ tự sau:

**Bước 1: Khởi động Database DB**
Mở postgres shell:
```sql
CREATE DATABASE hanhchinh_db;
\c hanhchinh_db
\i database/init.sql
```

**Bước 2: Cài Backend**
```bash
cd backend
Copy-Item .env.example .env # Chỉnh lại chuỗi kết nối DATABASE_URL nếu khác port.
npm install
npm run dev # -> Mở http://localhost:5000
```

**Bước 3: Cài Frontend**
```bash
cd frontend
npm install
npm run dev # -> Mở http://localhost:5173 hoặc 3000
```

**Bước 4: Cấp thiết lập AI Service**
```bash
cd ai-service
Copy-Item .env.example .env # Set DATABASE_URL và kẹp GEMINI_API_KEY
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
# Xây index (Option: Chỉ chạy 1 lần khi cấp mới data)
# python index_data.py
uvicorn main:app --port 8001 --reload # -> Mở http://localhost:8001
```
*Note: VS Code workspace đang lưu sẵn file tasks trong `.vscode` có thể cấu hình phím tắt cho `Run All` khởi chạy đồng loạt port Terminal.*

## 7. CƠ CHẾ HOẠT ĐỘNG CỦA RAG + CHATBOT
- **Nguồn cấp:** Module `crawler` điền data thô chuẩn vào Postgres (`procedures.raw_content`).
- **Nguồn xử lý Indexed:** `ai-service/index_data.py` bóc text lưu qua embedding lưu ẩn ChromaDB.
- **Luồng Truy Vấn (User Query):** 
  - Frontend gọi `POST http://localhost:5000/api/chat`
  - Backend forward sang `POST http://localhost:8001/chat` (AI Service)
  - AI Service so sánh khoảng cách Vector (Semantic Search) trong ChromaDB lấy top 3 kết quả, kết hợp Langchain sinh prompt dồn tới LLM (API Gemini). Cuối cùng trả về message kết luận minh bạch tới màng hình Frontend.

---
Tài liệu định hướng tổng hợp kiến thức toàn cục. Các developer / AI Agent có thể sử dụng thông tin file này như bản mô tả thiết kế đầy đủ mọi ngóc ngách của dự án.