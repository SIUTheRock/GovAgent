.PHONY: setup start stop clean help db-init data-import

help:
	@echo "Lệnh Makefile hỗ trợ (OLP 2025):"
	@echo "  make setup         - Cài đặt toàn bộ thư viện (Backend, Frontend, AI)"
	@echo "  make db-init       - Khởi tạo Database PostgreSQL"
	@echo "  make data-import   - Nhập dữ liệu mẫu"
	@echo "  make start         - Khởi chạy các dịch vụ ở chế độ nền"
	@echo "  make stop          - Dừng tất cả các dịch vụ"

setup:
	@echo "Cài đặt Backend..."
	@cd backend && npm install
	@echo "Cài đặt Frontend..."
	@cd frontend && npm install
	@echo "Thiết lập biến môi trường..."
	@cp backend/.env.example backend/.env 2>/dev/null || true
	@cp ai-service/.env.example ai-service/.env 2>/dev/null || true
	@echo "Cài đặt AI Service..."
	@cd ai-service && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	@echo "Hoàn thành!"

db-init:
	@echo "Khởi tạo cơ sở dữ liệu PostgreSQL..."
	@psql -U postgres -c "CREATE DATABASE hanhchinh_db;" || true
	@psql -U postgres -d hanhchinh_db -f database/init.sql

data-import:
	@echo "Tạo dữ liệu mẫu và nạp vào DB..."
	@cd crawler && python3 crawler.py --mode sample && python3 process_data.py
	@echo "Nạp dữ liệu vào ChromaDB..."
	@cd ai-service && . .venv/bin/activate && python3 index_data.py

start:
	@echo "Sử dụng docker-compose để khởi chạy dự án..."
	@docker-compose up -d --build

stop:
	@echo "Dừng các dịch vụ Docker..."
	@docker-compose down

clean:
	@echo "Dọn dẹp môi trường..."
	@rm -rf backend/node_modules frontend/node_modules ai-service/.venv