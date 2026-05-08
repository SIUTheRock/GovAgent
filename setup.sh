#!/bin/bash
# PPNCKH Setup Script for Linux/macOS
echo "Bắt đầu cài đặt môi trường cho dự án PPNCKH..."

# 1. Cài đặt Node modules
echo "[1/3] Cài đặt Node.js dependencies..."
cd backend && npm install
cd ../frontend && npm install
cd ..

# 2. Thiết lập biến môi trường cơ bản
echo "[2/4] Tạo file .env từ .env.example..."
cp backend/.env.example backend/.env 2>/dev/null || true
cp ai-service/.env.example ai-service/.env 2>/dev/null || true

# 3. Cài đặt Python Virtual Environment
echo "[3/4] Cài đặt Python dependencies cho AI-Service..."
cd ai-service
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
cd ..

echo "========================================="
echo "✅ Cài đặt hoàn tất!"
echo "Bước tiếp theo: Sửa file ai-service/.env (nhập GEMINI_API_KEY) rồi chạy 'make start' hoặc 'docker-compose up -d'"
echo "========================================="