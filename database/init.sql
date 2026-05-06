\encoding UTF8
-- ============================================================
-- Schema PostgreSQL - Hệ thống Tra cứu Thủ tục Hành chính
-- TP. Hồ Chí Minh
-- ============================================================

-- Lĩnh vực / Danh mục
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Thủ tục hành chính
CREATE TABLE IF NOT EXISTS procedures (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE,
    name VARCHAR(1000) NOT NULL,
    category_id INT REFERENCES categories(id) ON DELETE SET NULL,
    level VARCHAR(100),                      -- "Cấp tỉnh", "Cấp huyện", "Cấp xã"
    implementing_agency VARCHAR(500),        -- Cơ quan thực hiện
    processing_time VARCHAR(200),            -- Thời gian giải quyết
    fee TEXT,                                -- Lệ phí
    requirements TEXT,                       -- Điều kiện thực hiện
    procedure_steps TEXT,                    -- Trình tự thực hiện
    required_documents TEXT,                 -- Thành phần hồ sơ
    result TEXT,                             -- Kết quả thực hiện
    legal_basis TEXT,                        -- Căn cứ pháp lý
    source_url TEXT,                         -- URL nguồn gốc
    raw_content TEXT,                        -- Nội dung đầy đủ (dùng cho RAG)
    is_active BOOLEAN DEFAULT TRUE,
    view_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Full-text search index (tiếng Việt - dùng 'simple' vì PostgreSQL không có vi)
CREATE INDEX IF NOT EXISTS idx_procedures_fts
    ON procedures USING GIN (to_tsvector('simple', coalesce(name,'') || ' ' || coalesce(raw_content,'')));

CREATE INDEX IF NOT EXISTS idx_procedures_category ON procedures(category_id);
CREATE INDEX IF NOT EXISTS idx_procedures_level ON procedures(level);
CREATE INDEX IF NOT EXISTS idx_procedures_active ON procedures(is_active);

-- Lịch sử chat (analytics)
CREATE TABLE IF NOT EXISTS chat_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    question TEXT NOT NULL,
    answer TEXT,
    referenced_procedure_ids INT[],
    response_time_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_logs_session ON chat_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_created ON chat_logs(created_at);

-- Địa điểm / Cơ quan hành chính (cho Map)
CREATE TABLE IF NOT EXISTS agencies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    address TEXT,
    district VARCHAR(200),
    phone VARCHAR(50),
    email VARCHAR(200),
    website TEXT,
    lat DECIMAL(10, 8),
    lng DECIMAL(11, 8),
    category_ids INT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- Seed dữ liệu Danh mục mẫu
-- ============================================================
INSERT INTO categories (name, slug, description, icon) VALUES
('Hộ tịch', 'ho-tich', 'Đăng ký khai sinh, khai tử, kết hôn, nhận con nuôi...', '📋'),
('Cư trú', 'cu-tru', 'Đăng ký thường trú, tạm trú, tách hộ khẩu...', '🏠'),
('Đất đai - Nhà ở', 'dat-dai-nha-o', 'Cấp giấy chứng nhận quyền sử dụng đất, chuyển nhượng...', '🏡'),
('Doanh nghiệp', 'doanh-nghiep', 'Đăng ký kinh doanh, thay đổi thông tin doanh nghiệp...', '💼'),
('Giáo dục', 'giao-duc', 'Nhập học, chuyển trường, công nhận bằng cấp...', '🎓'),
('Y tế', 'y-te', 'Cấp giấy khám sức khỏe, đăng ký khám chữa bệnh...', '🏥'),
('Giao thông - Vận tải', 'giao-thong-van-tai', 'Đăng ký phương tiện, cấp bằng lái xe...', '🚗'),
('Xây dựng', 'xay-dung', 'Cấp phép xây dựng, thẩm định thiết kế...', '🏗️'),
('Lao động - Việc làm', 'lao-dong-viec-lam', 'Bảo hiểm xã hội, giải quyết việc làm...', '👷'),
('Tư pháp', 'tu-phap', 'Công chứng, chứng thực, lý lịch tư pháp...', '⚖️')
ON CONFLICT (slug) DO NOTHING;
