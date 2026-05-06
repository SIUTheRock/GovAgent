# =====================================================
# Script khởi động local development (không dùng Docker)
# Yêu cầu: Node.js, Python 3.12, PostgreSQL đang chạy
# =====================================================

Write-Host "=== Khởi động TTHC TP.HCM - Local Dev ===" -ForegroundColor Cyan

# Kiểm tra PostgreSQL
Write-Host "`n[1] Kiểm tra PostgreSQL..." -ForegroundColor Yellow
$pg = Get-Process -Name "postgres" -ErrorAction SilentlyContinue
if (-not $pg) {
    Write-Host "    PostgreSQL chưa chạy. Hãy khởi động PostgreSQL trước." -ForegroundColor Red
    Write-Host "    Lệnh: pg_ctl start -D 'C:\Program Files\PostgreSQL\16\data'" -ForegroundColor Gray
} else {
    Write-Host "    PostgreSQL đang chạy." -ForegroundColor Green
}

# Khởi tạo database (chỉ cần chạy lần đầu)
Write-Host "`n[2] Khởi tạo database (bỏ qua nếu đã có)..." -ForegroundColor Yellow
Write-Host "    Chạy: psql -U postgres -c 'CREATE DATABASE hanhchinh_db;' (nếu chưa tạo DB)" -ForegroundColor Gray
Write-Host "    Chạy: psql -U postgres -d hanhchinh_db -f database\init.sql" -ForegroundColor Gray

# Cài đặt Python venv cho AI service
Write-Host "`n[3] Cài đặt môi trường Python (lần đầu)..." -ForegroundColor Yellow
if (-not (Test-Path "ai-service\.venv")) {
    Write-Host "    Tạo virtualenv..." -ForegroundColor Gray
    py -m venv ai-service\.venv
    & "ai-service\.venv\Scripts\pip" install -r ai-service\requirements.txt
    Write-Host "    Đã cài xong Python deps." -ForegroundColor Green
} else {
    Write-Host "    Virtualenv đã tồn tại, bỏ qua." -ForegroundColor Green
}

# Copy .env nếu chưa có
if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "[Info] Đã tạo backend/.env từ .env.example" -ForegroundColor Cyan
}
if (-not (Test-Path "ai-service\.env")) {
    Copy-Item "ai-service\.env.example" "ai-service\.env"
    Write-Host "[Info] Đã tạo ai-service/.env từ .env.example" -ForegroundColor Cyan
    Write-Host "[!] Hãy điền GEMINI_API_KEY vào ai-service/.env" -ForegroundColor Yellow
}

Write-Host "`n=== Hướng dẫn khởi động ===" -ForegroundColor Cyan
Write-Host "Mở 3 terminal riêng biệt và chạy các lệnh sau:" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 1 - Backend:" -ForegroundColor Green
Write-Host "  cd backend; npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "Terminal 2 - AI Service:" -ForegroundColor Green
Write-Host "  cd ai-service; .\.venv\Scripts\activate; uvicorn main:app --reload --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "Terminal 3 - Frontend:" -ForegroundColor Green
Write-Host "  cd frontend; npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "Sau đó mở: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "=== Import dữ liệu mẫu (lần đầu) ===" -ForegroundColor Cyan
Write-Host "1. Tạo dữ liệu mẫu:  cd crawler; py crawler.py --mode sample" -ForegroundColor Gray
Write-Host "2. Nhập vào DB:       cd crawler; py process_data.py" -ForegroundColor Gray
Write-Host "3. Index vào ChromaDB: cd ai-service; .\.venv\Scripts\activate; py index_data.py" -ForegroundColor Gray
