-- ============================================================================
-- RETAIL SITE SELECTION DECISION SUPPORT SYSTEM - UPDATED DATABASE SCHEMA
-- Thêm bảng evaluation_result để lưu trữ kết quả phân tích riêng biệt
-- ============================================================================
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Drop existing tables if they exist (theo thứ tự phụ thuộc)
DROP TABLE IF EXISTS evaluation_result;
DROP TABLE IF EXISTS potential_site;
DROP TABLE IF EXISTS expert_criteria_config;
DROP TABLE IF EXISTS district;
DROP TABLE IF EXISTS users;

-- ============================================================================
-- 1. USERS TABLE
-- Quản lý người dùng hệ thống
-- ============================================================================
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE COMMENT 'Tên đăng nhập',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Mật khẩu đã mã hóa',
    full_name VARCHAR(255) COMMENT 'Họ và tên đầy đủ',
    role VARCHAR(50) DEFAULT 'STORE_OWNER' COMMENT 'Vai trò: STORE_OWNER, ADMIN, ANALYST',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng quản lý người dùng hệ thống';

-- ============================================================================
-- 2. DISTRICT TABLE
-- Quản lý thông tin các quận/huyện
-- ============================================================================
CREATE TABLE district (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL COMMENT 'Tên Quận/Huyện',
    x_coordinate DOUBLE COMMENT 'Kinh độ trung tâm quận',
    y_coordinate DOUBLE COMMENT 'Vĩ độ trung tâm quận',
    population_density DOUBLE COMMENT 'Mật độ dân số trung bình (người/km²)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_district_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng quản lý thông tin quận/huyện';

-- ============================================================================
-- 3. EXPERT CRITERIA CONFIG TABLE
-- Lưu trữ các cấu hình trọng số chuyên gia cho thuật toán MCDM
-- ============================================================================
CREATE TABLE expert_criteria_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    strategy_name VARCHAR(255) NOT NULL COMMENT 'Tên chiến lược',
    description TEXT COMMENT 'Mô tả chiến lược',
    
    -- Trọng số cho các tiêu chí COST
    weight_rent_cost DOUBLE NOT NULL DEFAULT 0.15 COMMENT 'Trọng số giá thuê (Cost)',
    weight_renovation_cost DOUBLE NOT NULL DEFAULT 0.10 COMMENT 'Trọng số chi phí sửa chữa (Cost)',
    weight_competitor_count DOUBLE NOT NULL DEFAULT 0.15 COMMENT 'Trọng số số lượng đối thủ (Cost)',
    weight_warehouse_distance DOUBLE NOT NULL DEFAULT 0.10 COMMENT 'Trọng số khoảng cách kho (Cost)',
    
    -- Trọng số cho các tiêu chí BENEFIT
    weight_floor_area DOUBLE NOT NULL DEFAULT 0.15 COMMENT 'Trọng số diện tích sàn (Benefit)',
    weight_front_width DOUBLE NOT NULL DEFAULT 0.10 COMMENT 'Trọng số mặt tiền (Benefit)',
    weight_traffic_score DOUBLE NOT NULL DEFAULT 0.15 COMMENT 'Trọng số lưu lượng giao thông (Benefit)',
    weight_population_density DOUBLE NOT NULL DEFAULT 0.10 COMMENT 'Trọng số mật độ dân cư (Benefit)',
    
    -- Metadata
    is_active BOOLEAN DEFAULT FALSE COMMENT 'Cấu hình đang được sử dụng',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) COMMENT 'Người tạo cấu hình',
    
    -- Constraint: Tổng trọng số phải = 1.0
    CONSTRAINT chk_weights_sum CHECK (
        ROUND(weight_rent_cost + weight_renovation_cost + weight_competitor_count + 
              weight_warehouse_distance + weight_floor_area + weight_front_width + 
              weight_traffic_score + weight_population_density, 2) = 1.0
    ),
    
    INDEX idx_active_config (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng cấu hình trọng số chuyên gia';

-- ============================================================================
-- 4. POTENTIAL SITE TABLE (CẬP NHẬT - BỎ CÁC TRƯỜNG KẾT QUẢ TOPSIS)
-- Bảng chính lưu trữ dữ liệu các địa điểm ứng viên - CHỈ CHỨA DỮ LIỆU ĐẦU VÀO
-- ============================================================================
CREATE TABLE potential_site (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    site_code VARCHAR(50) UNIQUE COMMENT 'Mã định danh địa điểm (VD: HN-Q1-001)',
    
    -- Thông tin địa lý
    address VARCHAR(500) NOT NULL COMMENT 'Địa chỉ chi tiết',
    district_id BIGINT NOT NULL COMMENT 'Quận/Huyện',
    x_coordinate DOUBLE COMMENT 'Kinh độ',
    y_coordinate DOUBLE COMMENT 'Vĩ độ',
    
    -- ========================================================================
    -- NHÓM COST CRITERIA (Càng thấp càng tốt)
    -- ========================================================================
    rent_cost DOUBLE NOT NULL COMMENT 'Giá thuê hàng tháng (triệu VND)',
    renovation_cost DOUBLE NOT NULL COMMENT 'Chi phí sửa chữa/setup ban đầu (triệu VND)',
    competitor_count INT NOT NULL COMMENT 'Số lượng đối thủ trong bán kính 500m',
    distance_to_warehouse DOUBLE NOT NULL COMMENT 'Khoảng cách đến kho trung tâm (km)',
    
    -- ========================================================================
    -- NHÓM BENEFIT CRITERIA (Càng cao càng tốt)
    -- ========================================================================
    floor_area DOUBLE NOT NULL COMMENT 'Diện tích sàn kinh doanh (m²)',
    front_width DOUBLE NOT NULL COMMENT 'Chiều rộng mặt tiền (m)',
    traffic_score INT NOT NULL COMMENT 'Điểm lưu lượng giao thông (1-10)',
    population_density DOUBLE NOT NULL COMMENT 'Mật độ dân cư bán kính 500m (người/km²)',
    
    -- ========================================================================
    -- THUỘC TÍNH BỔ SUNG
    -- ========================================================================
    has_parking BOOLEAN DEFAULT FALSE COMMENT 'Có chỗ đỗ xe',
    is_corner_lot BOOLEAN DEFAULT FALSE COMMENT 'Là lô góc (2 mặt tiền)',
    near_school BOOLEAN DEFAULT FALSE COMMENT 'Gần trường học',
    near_market BOOLEAN DEFAULT FALSE COMMENT 'Gần chợ truyền thống',
    
    -- Metadata
    status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT 'ACTIVE, RENTED, REJECTED',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes TEXT COMMENT 'Ghi chú bổ sung',
    
    FOREIGN KEY (district_id) REFERENCES district(id),
    
    INDEX idx_district (district_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng lưu trữ các địa điểm ứng viên (chỉ dữ liệu đầu vào)';

-- ============================================================================
-- 5. EVALUATION RESULT TABLE (MỚI)
-- Bảng lưu trữ kết quả phân tích MCDM cho từng lần chạy
-- ============================================================================
CREATE TABLE evaluation_result (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- Liên kết
    user_id BIGINT COMMENT 'Người thực hiện đánh giá',
    config_id BIGINT NOT NULL COMMENT 'Cấu hình trọng số được sử dụng',
    site_id BIGINT NOT NULL COMMENT 'Địa điểm được đánh giá',
    
    -- Kết quả phân tích
    algorithm_used VARCHAR(50) DEFAULT 'TOPSIS' COMMENT 'Thuật toán được sử dụng: TOPSIS, AHP, ELECTRE',
    topsis_score DOUBLE NOT NULL COMMENT 'Điểm TOPSIS (0-1, càng cao càng tốt)',
    rank_position INT NOT NULL COMMENT 'Thứ hạng trong lần phân tích này',
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời điểm phân tích',
    execution_time_ms BIGINT COMMENT 'Thời gian thực thi (milliseconds)',
    batch_id VARCHAR(100) COMMENT 'ID của batch phân tích (để group các kết quả cùng lần chạy)',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (config_id) REFERENCES expert_criteria_config(id),
    FOREIGN KEY (site_id) REFERENCES potential_site(id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_config_id (config_id),
    INDEX idx_site_id (site_id),
    INDEX idx_batch_id (batch_id),
    INDEX idx_rank (rank_position),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_score (topsis_score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng lưu trữ kết quả phân tích MCDM';

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Sample Users
INSERT INTO users (username, password_hash, full_name, role) VALUES
('admin', '$2a$10$dummyhash123456789', 'System Administrator', 'ADMIN'),
('analyst1', '$2a$10$dummyhash123456789', 'Business Analyst', 'ANALYST'),
('owner1', '$2a$10$dummyhash123456789', 'Store Owner Demo', 'STORE_OWNER');

-- Sample Districts
INSERT INTO district (name, x_coordinate, y_coordinate, population_density) VALUES
('Quận 1', 106.6980, 10.7758, 38000),
('Quận 2', 106.7314, 10.7812, 12000),
('Quận 3', 106.6835, 10.7835, 32000),
('Quận 4', 106.7032, 10.7586, 28000),
('Quận 5', 106.6628, 10.7556, 35000),
('Quận 6', 106.6334, 10.7475, 25000),
('Quận 7', 106.7221, 10.7362, 15000),
('Quận 8', 106.6588, 10.7278, 20000),
('Quận 10', 106.6683, 10.7724, 30000),
('Quận 11', 106.6431, 10.7645, 27000);

-- Sample Expert Criteria Configs
INSERT INTO expert_criteria_config (
    strategy_name, description,
    weight_rent_cost, weight_renovation_cost, weight_competitor_count, weight_warehouse_distance,
    weight_floor_area, weight_front_width, weight_traffic_score, weight_population_density,
    is_active, created_by
) VALUES 
(
    'Phủ Sóng Thị Trường',
    'Ưu tiên vị trí có lưu lượng cao, mật độ dân cư cao. Chấp nhận giá thuê và cạnh tranh cao.',
    0.08, 0.07, 0.10, 0.05,
    0.12, 0.10, 0.25, 0.23,
    TRUE, 'Strategy Team'
),
(
    'Tối Ưu Lợi Nhuận',
    'Ưu tiên chi phí thấp, ít đối thủ cạnh tranh.',
    0.25, 0.15, 0.20, 0.10,
    0.10, 0.05, 0.08, 0.07,
    FALSE, 'Finance Team'
),
(
    'Cân Bằng Toàn Diện',
    'Cân đối giữa chi phí và lợi ích.',
    0.15, 0.10, 0.12, 0.08,
    0.15, 0.10, 0.15, 0.15,
    FALSE, 'Operations Team'
);

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- View: Kết quả phân tích mới nhất cho mỗi site
CREATE OR REPLACE VIEW vw_latest_evaluation AS
SELECT 
    er.*,
    ps.site_code,
    ps.address,
    d.name as district_name,
    ec.strategy_name,
    u.full_name as evaluated_by
FROM evaluation_result er
INNER JOIN (
    SELECT site_id, MAX(created_at) as max_date
    FROM evaluation_result
    GROUP BY site_id
) latest ON er.site_id = latest.site_id AND er.created_at = latest.max_date
LEFT JOIN potential_site ps ON er.site_id = ps.id
LEFT JOIN district d ON ps.district_id = d.id
LEFT JOIN expert_criteria_config ec ON er.config_id = ec.id
LEFT JOIN users u ON er.user_id = u.id;

-- View: Top 10 địa điểm từ batch phân tích mới nhất
CREATE OR REPLACE VIEW vw_top_sites_latest_batch AS
SELECT 
    er.rank_position,
    ps.site_code,
    ps.address,
    d.name as district_name,
    er.topsis_score,
    ps.rent_cost,
    ps.floor_area,
    ps.traffic_score,
    ps.competitor_count,
    ec.strategy_name,
    er.created_at as analysis_date
FROM evaluation_result er
INNER JOIN (
    SELECT MAX(batch_id) as latest_batch FROM evaluation_result
) lb ON er.batch_id = lb.latest_batch
LEFT JOIN potential_site ps ON er.site_id = ps.id
LEFT JOIN district d ON ps.district_id = d.id
LEFT JOIN expert_criteria_config ec ON er.config_id = ec.id
WHERE er.rank_position <= 10
ORDER BY er.rank_position ASC;

-- View: Thống kê theo quận (dựa trên kết quả mới nhất)
CREATE OR REPLACE VIEW vw_district_summary AS
SELECT 
    d.name as district_name,
    COUNT(DISTINCT ps.id) as total_sites,
    AVG(er.topsis_score) as avg_topsis_score,
    AVG(ps.rent_cost) as avg_rent_cost,
    AVG(ps.floor_area) as avg_floor_area,
    MIN(er.rank_position) as best_rank
FROM district d
LEFT JOIN potential_site ps ON d.id = ps.district_id AND ps.status = 'ACTIVE'
LEFT JOIN evaluation_result er ON ps.id = er.site_id
    AND er.created_at = (
        SELECT MAX(created_at) 
        FROM evaluation_result 
        WHERE site_id = ps.id
    )
GROUP BY d.id, d.name
ORDER BY avg_topsis_score DESC;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
