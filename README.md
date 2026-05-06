# PPNCKH - Tra cứu Thủ tục Hành chính TP.HCM

## Cấu trúc dự án

```
PPNCKH/
├── frontend/          # React 18 + TailwindCSS + React Router
├── backend/           # Node.js + Express.js REST API  
├── ai-service/        # Python FastAPI + LangChain RAG
├── crawler/           # Playwright crawler + data processing
├── database/          # PostgreSQL schema
├── docker-compose.yml
└── start-dev.ps1      # Script hướng dẫn khởi động
```

## Khởi động nhanh

### Yêu cầu
- Node.js 20+
- Python 3.12+
- PostgreSQL 16

### Bước 1: Chuẩn bị database
```bash
psql -U postgres -c "CREATE DATABASE hanhchinh_db;"
psql -U postgres -d hanhchinh_db -f database/init.sql
```

### Bước 2: Cấu hình environment
```bash
# Backend
copy backend\.env.example backend\.env

# AI Service - điền API key
copy ai-service\.env.example ai-service\.env
# Sửa GEMINI_API_KEY trong ai-service/.env
```

### Bước 3: Cài dependencies
```bash
cd backend && npm install
cd frontend && npm install
cd ai-service && py -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
```

### Bước 4: Import dữ liệu mẫu
```bash
cd crawler
py crawler.py --mode sample   # Tạo dữ liệu mẫu
py process_data.py             # Nhập vào PostgreSQL

cd ../ai-service
.venv\Scripts\activate
py index_data.py               # Nạp vào ChromaDB
```

### Bước 5: Khởi động các service
```bash
# Terminal 1 - Backend (port 5000)
cd backend && npm run dev

# Terminal 2 - AI Service (port 8000)
cd ai-service && .venv\Scripts\activate && uvicorn main:app --reload --port 8000

# Terminal 3 - Frontend (port 3000)
cd frontend && npm run dev
```

Mở trình duyệt: **http://localhost:3000**

## API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/categories` | Danh sách lĩnh vực |
| GET | `/api/procedures?page=1&limit=12&category=&level=` | Danh sách thủ tục |
| GET | `/api/procedures/:id` | Chi tiết thủ tục |
| GET | `/api/search?q=&category=` | Tìm kiếm full-text |
| POST | `/api/chat` | Chat với AI `{ question, session_id }` |

## Tech Stack

| Layer | Công nghệ |
|-------|-----------|
| Frontend | React 18, TailwindCSS, React Router, Axios |
| Backend | Node.js 24, Express.js, PostgreSQL |
| AI/RAG | Python 3.12, FastAPI, LangChain, ChromaDB |
| Embedding | paraphrase-multilingual-MiniLM-L12-v2 |
| LLM | Google Gemini 1.5 Flash |
| Crawler | Playwright, BeautifulSoup4 |
