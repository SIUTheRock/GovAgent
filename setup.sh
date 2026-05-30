#!/bin/bash
# =========================================================
# Script cài đặt môi trường PPNCKH (Linux / macOS / WSL)
# Tương thích kiến trúc: Node.js (Frontend & Backend), Python (AI Service)
# =========================================================

# Khởi tạo màu sắc
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== BẮT ĐẦU CÀI ĐẶT MÔI TRƯỜNG DỰ ÁN PPNCKH ===${NC}\n"

# 1. Cài đặt Backend Node modules
echo -e "${YELLOW}[1/4] Cài đặt Node.js dependencies cho Backend...${NC}"
cd backend || exit
npm install
cd ..

# 2. Cài đặt Frontend Node modules
echo -e "${YELLOW}[2/4] Cài đặt Node.js dependencies cho Frontend...${NC}"
cd frontend || exit
npm install
cd ..

# 3. Thiết lập biến môi trường cơ bản
echo -e "\n${YELLOW}[3/4] Cấu hình file biến môi trường (.env)...${NC}"
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env 2>/dev/null || echo -e "  => Đã tạo backend/.env. Vui lòng cập nhật thông tin DATABASE_URL."
fi

if [ ! -f "ai-service/.env" ]; then
    cp ai-service/.env.example ai-service/.env 2>/dev/null || echo -e "  => Đã tạo ai-service/.env. Vui lòng bổ sung GEMINI_API_KEY."
fi

# 4. Cài đặt Python Virtual Environment (AI Service)
echo -e "\n${YELLOW}[4/4] Cài đặt nền tảng Python (Virtual Environment) cho AI-Service...${NC}"
cd ai-service || exit
if [ ! -d ".venv" ]; then
    echo "  => Tạo môi trường ảo .venv..."
    python3 -m venv .venv
fi
echo "  => Kích hoạt .venv và cài đặt thư viện..."
source .venv/bin/activate
pip install -r requirements.txt
cd ..

# Hoàn tất và Hướng dẫn
echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN}✅ CÀI ĐẶT MÔI TRƯỜNG CƠ BẢN HOÀN TẤT!${NC}"
echo -e "================================================================\n"

echo -e "Các bước tiếp theo cần thực hiện:"
echo -e "  1. Mở file ${CYAN}ai-service/.env${NC} và điền ${YELLOW}GEMINI_API_KEY${NC} của bạn."
echo -e "  2. Mở file ${CYAN}backend/.env${NC} và kiểm tra/cấu hình ${YELLOW}DATABASE_URL${NC}."
echo -e "  3. Khởi tạo Database nếu dùng Local:"
echo -e "     $ psql -U postgres -c \"CREATE DATABASE hanhchinh_db;\""
echo -e "     $ psql -U postgres -d hanhchinh_db -f database/init.sql"
echo -e "  4. Chạy toàn bộ hệ thống bằng Docker tương thích:"
echo -e "     $ docker-compose up -d --build"
echo -e "     hoặc chạy qua lệnh Makefile:"
echo -e "     $ make start"
echo -e "\nChúc bạn lập trình và trải nghiệm hệ thống vui vẻ!"