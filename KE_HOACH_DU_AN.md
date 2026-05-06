# KẾ HOẠCH DỰ ÁN
## Ứng dụng Trợ lý Ảo Hỗ trợ Tra cứu Thủ tục Hành chính Công
### TP. Hồ Chí Minh

---

## 1. TỔNG QUAN DỰ ÁN

| Hạng mục | Chi tiết |
|---|---|
| **Tên đề tài** | Ứng dụng trợ lý ảo hỗ trợ tra cứu thủ tục hành chính công để tối ưu hóa quy trình phục vụ người dân tại Tp.HCM |
| **Loại sản phẩm** | Web App (nghiên cứu + sản phẩm thực tế) |
| **Thời gian dự kiến** | 8–10 tuần |

---

## 2. CÔNG NGHỆ SỬ DỤNG (TECH STACK)

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│            React + TailwindCSS + Axios                      │
├─────────────────────────────────────────────────────────────┤
│                     BACKEND CHÍNH                           │
│              Node.js + Express.js + REST API                │
├───────────────────────────┬─────────────────────────────────┤
│       AI SERVICE          │         DATABASE                │
│  Python FastAPI           │  PostgreSQL (thủ tục, tài liệu) │
│  LangChain + RAG          │  ChromaDB (vector embeddings)   │
│  OpenAI Embeddings        │                                 │
├───────────────────────────┴─────────────────────────────────┤
│                    DATA COLLECTION                          │
│         Web Crawler (Scrapy / Playwright) crawl từng        │
│    dichvucong.gov.vn (cổng dịch vụ công quốc gia, lọc TP.HCM) │
└─────────────────────────────────────────────────────────────┘
```

### Chi tiết từng thành phần:

| Thành phần | Công nghệ | Ghi chú |
|---|---|---|
| Frontend | React 18, TailwindCSS, React Router | SPA |
| Backend API | Node.js 20, Express.js | REST API |
| AI / RAG Service | Python 3.11, FastAPI, LangChain | Microservice riêng |
| LLM | Gemini API hoặc OpenAI GPT-3.5-turbo | Cần API key |
| Embedding | `text-embedding-3-small` (OpenAI) hoặc `all-MiniLM-L6-v2` (free) | Cho RAG |
| Vector DB | ChromaDB (local, miễn phí) | Lưu embeddings thủ tục |
| Relational DB | PostgreSQL 16 | Thủ tục, metadata |
| Crawler | Scrapy + Playwright | Thu thập dữ liệu |
| Deploy | Localhost (Docker Compose) | Demo |

---

## 3. KIẾN TRÚC HỆ THỐNG

```
User (Browser)
     │
     ▼
React Frontend (port 3000)
     │  HTTP / Axios
     ▼
Node.js Express API (port 5000)
  ├── /api/procedures   → PostgreSQL
  ├── /api/search       → PostgreSQL Full-text search
  ├── /api/chat         → forward to AI Service
  └── /api/news         → [optional]
     │
     ▼
Python FastAPI AI Service (port 8000)
  └── /chat  → LangChain RAG Pipeline
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
     ChromaDB             LLM (Gemini/GPT)
  (vector search)      (generate answer)
```

### RAG Pipeline (luồng chatbot):
```
Câu hỏi người dùng
        │
        ▼
Embedding câu hỏi (embedding model)
        │
        ▼
Vector Search trong ChromaDB
(tìm top-K đoạn văn liên quan nhất)
        │
        ▼
Tạo Prompt = [System Prompt] + [Context từ ChromaDB] + [Câu hỏi]
        │
        ▼
Gửi tới LLM (Gemini / GPT)
        │
        ▼
Trả lời + danh sách tài liệu gợi ý
```

---

## 4. CẤU TRÚC THƯ MỤC DỰ ÁN

```
PPNCKH/
├── frontend/               # React App
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Chat.jsx
│   │   │   ├── Documents.jsx
│   │   │   ├── ProcedureDetail.jsx
│   │   │   ├── Map.jsx         (optional)
│   │   │   └── News.jsx        (optional)
│   │   ├── components/
│   │   │   ├── ChatBox.jsx
│   │   │   ├── ProcedureCard.jsx
│   │   │   ├── SearchBar.jsx
│   │   │   └── Navbar.jsx
│   │   └── services/
│   │       └── api.js
│   └── package.json
│
├── backend/                # Node.js Express
│   ├── src/
│   │   ├── routes/
│   │   │   ├── procedures.js
│   │   │   ├── search.js
│   │   │   ├── chat.js
│   │   │   └── news.js
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── db/
│   │   │   └── postgres.js
│   │   └── app.js
│   └── package.json
│
├── ai-service/             # Python FastAPI + LangChain
│   ├── main.py
│   ├── rag/
│   │   ├── chain.py        # LangChain RAG pipeline
│   │   ├── embeddings.py   # Embedding logic
│   │   └── vectorstore.py  # ChromaDB management
│   ├── data/
│   │   └── chroma_db/      # ChromaDB files
│   └── requirements.txt
│
├── crawler/                # Thu thập dữ liệu
│   ├── spiders/
│   │   └── dichvucong_spider.py
│   ├── data/
│   │   └── procedures.json
│   └── requirements.txt
│
├── database/
│   └── init.sql            # Schema PostgreSQL
│
├── docker-compose.yml
└── KE_HOACH_DU_AN.md
```

---

## 5. DATABASE SCHEMA (PostgreSQL)

```sql
-- Lĩnh vực hành chính
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,         -- "Hộ tịch", "Đất đai", "Doanh nghiệp"...
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Thủ tục hành chính
CREATE TABLE procedures (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE,           -- Mã thủ tục
    name VARCHAR(500) NOT NULL,         -- Tên thủ tục
    category_id INT REFERENCES categories(id),
    level VARCHAR(50),                  -- "Cấp tỉnh", "Cấp huyện", "Cấp xã"
    implementing_agency VARCHAR(255),   -- Cơ quan thực hiện
    processing_time VARCHAR(100),       -- Thời gian giải quyết
    fee TEXT,                           -- Lệ phí
    requirements TEXT,                  -- Điều kiện thực hiện
    procedure_steps TEXT,               -- Các bước thực hiện
    required_documents TEXT,            -- Thành phần hồ sơ
    result TEXT,                        -- Kết quả thực hiện
    legal_basis TEXT,                   -- Căn cứ pháp lý
    source_url TEXT,                    -- URL nguồn
    raw_content TEXT,                   -- Nội dung gốc (cho RAG)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Lịch sử chat (optional, lưu để phân tích)
CREATE TABLE chat_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    question TEXT NOT NULL,
    answer TEXT,
    referenced_procedure_ids INT[],
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 6. CÁC TRANG UI VÀ CHỨC NĂNG

### Trang 1: Trang chủ (`/`)
- Banner giới thiệu hệ thống
- Ô tìm kiếm nhanh thủ tục
- Danh sách lĩnh vực (categories)
- Nút truy cập nhanh vào Chatbot

### Trang 2: Chatbot (`/chat`)
- Giao diện hộp chat (bubble messages)
- Typing indicator khi AI đang xử lý
- Hiển thị tài liệu gợi ý kèm theo câu trả lời
- Click tài liệu → điều hướng sang trang Documents

### Trang 3: Danh sách Thủ tục (`/documents`)
- Bộ lọc: theo lĩnh vực, cấp thực hiện
- Thanh tìm kiếm full-text
- Danh sách thủ tục dạng card
- Phân trang

### Trang 4: Chi tiết Thủ tục (`/documents/:id`)
- Tên thủ tục, cơ quan, thời gian
- Các bước thực hiện
- Danh sách giấy tờ cần nộp
- Căn cứ pháp lý
- Link nguồn gốc

### Trang 5: Bản đồ - Map (`/map`) *(Optional)*
- Google Maps / Leaflet.js
- Tra cứu cơ quan hành chính gần nhất

### Trang 6: Tin tức (`/news`) *(Optional)*
- Tin tức về cải cách hành chính TP.HCM

---

## 7. KẾ HOẠCH THỰC HIỆN (Timeline)

### PHASE 1 — Khởi tạo & Hạ tầng (Tuần 1)
| Task | Mô tả |
|---|---|
| 1.1 | Cài đặt môi trường: Node.js, Python, PostgreSQL, Docker |
| 1.2 | Khởi tạo project React (Vite) |
| 1.3 | Khởi tạo Node.js Express server |
| 1.4 | Khởi tạo Python FastAPI AI service |
| 1.5 | Tạo schema PostgreSQL, kết nối DB |
| 1.6 | Cấu hình Docker Compose (chạy local) |

### PHASE 2 — Thu thập & Xử lý Dữ liệu (Tuần 1–2)
| Task | Mô tả |
|---|---|
| 2.1 | Nghiên cứu cấu trúc trang dichvucong.gov.vn (lọc theo địa phương TP.HCM) |
| 2.2 | Viết crawler thu thập danh sách thủ tục |
| 2.3 | Viết crawler thu thập nội dung chi tiết từng thủ tục |
| 2.4 | Làm sạch & chuẩn hóa dữ liệu (JSON → PostgreSQL) |
| 2.5 | Tạo embeddings và nạp vào ChromaDB |

### PHASE 3 — Backend API (Tuần 2–3)
| Task | Mô tả |
|---|---|
| 3.1 | API `GET /api/procedures` — danh sách, phân trang, filter |
| 3.2 | API `GET /api/procedures/:id` — chi tiết thủ tục |
| 3.3 | API `GET /api/search?q=` — tìm kiếm full-text PostgreSQL |
| 3.4 | API `POST /api/chat` — proxy sang AI service |
| 3.5 | API `GET /api/categories` — danh sách lĩnh vực |

### PHASE 4 — AI Service / RAG (Tuần 3)
| Task | Mô tả |
|---|---|
| 4.1 | Cài đặt LangChain, ChromaDB, embedding model |
| 4.2 | Xây dựng RAG chain (retriever + prompt + LLM) |
| 4.3 | Viết system prompt cho chatbot hành chính |
| 4.4 | API `POST /chat` trả về answer + danh sách procedure IDs |
| 4.5 | Kiểm thử RAG với bộ câu hỏi mẫu |

### PHASE 5 — Frontend (Tuần 4)
| Task | Mô tả |
|---|---|
| 5.1 | Setup React Router, layout chung, Navbar |
| 5.2 | Xây dựng trang Home |
| 5.3 | Xây dựng trang Chatbot (ChatBox component) |
| 5.4 | Xây dựng trang Documents (danh sách + filter) |
| 5.5 | Xây dựng trang chi tiết Procedure |
| 5.6 | Kết nối API với backend (Axios) |
| 5.7 | UI/UX responsive (TailwindCSS) |

### PHASE 6 — Kiểm thử & Đánh giá (Tuần 5)
| Task | Mô tả |
|---|---|
| 6.1 | Xây dựng bộ test câu hỏi (30–50 câu) |
| 6.2 | Đánh giá RAG: Precision, Recall, NDCG |
| 6.3 | Đánh giá chatbot: BLEU / ROUGE hoặc human eval |
| 6.4 | Kiểm thử tích hợp end-to-end |
| 6.5 | Fix bug, tối ưu tốc độ |

### PHASE 7 — Hoàn thiện & Báo cáo (Tuần 6)
| Task | Mô tả |
|---|---|
| 7.1 | Viết báo cáo nghiên cứu (background, methodology, results) |
| 7.2 | Hoàn thiện tài liệu kỹ thuật |
| 7.3 | Demo video / slide thuyết trình |
| 7.4 | Review và nộp |

---

## 8. CÁC RỦI RO & PHƯƠNG ÁN DỰ PHÒNG

| Rủi ro | Mức độ | Phương án |
|---|---|---|
| Trang dichvucong bị block crawler | Cao | Dùng Playwright giả lập trình duyệt; hoặc dùng dữ liệu mẫu thủ công |
| API key LLM tốn phí | Trung bình | Dùng model miễn phí: Google Gemini free tier hoặc Ollama (local) |
| Chất lượng RAG kém | Trung bình | Tinh chỉnh prompt, tăng chunk size, thêm metadata filtering |
| Dữ liệu không đủ phong phú | Thấp | Bổ sung từ văn bản pháp luật, thông tư liên quan |

---

## 9. PHÂN CHIA TRÁCH NHIỆM (nếu nhóm)

| Module | Người phụ trách | Ghi chú |
|---|---|---|
| Data Crawler | — | Python, Scrapy/Playwright |
| Backend API | — | Node.js Express |
| AI / RAG Service | — | Python, LangChain |
| Frontend | — | React, TailwindCSS |
| Báo cáo nghiên cứu | — | |

---

## 10. TIÊU CHÍ ĐÁNH GIÁ THÀNH CÔNG

### Về sản phẩm:
- [ ] Chatbot trả lời đúng ≥ 80% câu hỏi về thủ tục hành chính
- [ ] Thời gian phản hồi chatbot < 5 giây
- [ ] Hệ thống tải được ít nhất 500 thủ tục
- [ ] UI hoạt động trên mobile và desktop

### Về nghiên cứu:
- [ ] So sánh được hiệu quả RAG vs keyword search
- [ ] Có bộ dataset đánh giá (ground truth Q&A)
- [ ] Báo cáo có phần phân tích định lượng

---

## 11. BƯỚC TIẾP THEO NGAY BÂY GIỜ

1. **Tạo cấu trúc thư mục** dự án
2. **Khởi tạo** 3 project: `frontend/`, `backend/`, `ai-service/`
3. **Khởi tạo** PostgreSQL schema
4. **Nghiên cứu** cấu trúc trang dichvucong.gov.vn (filter TP.HCM) để lên kế hoạch crawler

---

*Cập nhật lần cuối: 26/04/2026*
