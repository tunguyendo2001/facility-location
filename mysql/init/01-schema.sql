-- ============================================================================
-- RETAIL SITE SELECTION DECISION SUPPORT SYSTEM - DATABASE SCHEMA
-- Hệ thống hỗ trợ quyết định chọn địa điểm mở siêu thị mini sử dụng TOPSIS
-- ============================================================================
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS potential_site;
DROP TABLE IF EXISTS expert_criteria_config;
DROP TABLE IF EXISTS district;

-- ============================================================================
-- 1. DISTRICT TABLE
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
-- 2. EXPERT CRITERIA CONFIG TABLE
-- Lưu trữ các cấu hình trọng số chuyên gia cho thuật toán TOPSIS
-- Mỗi cấu hình đại diện cho một chiến lược kinh doanh khác nhau
-- ============================================================================
CREATE TABLE expert_criteria_config (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    strategy_name VARCHAR(255) NOT NULL COMMENT 'Tên chiến lược (VD: "Phủ sóng thị trường", "Tối ưu lợi nhuận")',
    description TEXT COMMENT 'Mô tả chiến lược',
    
    -- Trọng số cho các tiêu chí COST (tổng weight_cost phải = 0.5 trong ví dụ cân bằng)
    weight_rent_cost DOUBLE NOT NULL DEFAULT 0.15 COMMENT 'Trọng số giá thuê (Cost)',
    weight_renovation_cost DOUBLE NOT NULL DEFAULT 0.10 COMMENT 'Trọng số chi phí sửa chữa (Cost)',
    weight_competitor_count DOUBLE NOT NULL DEFAULT 0.15 COMMENT 'Trọng số số lượng đối thủ (Cost)',
    weight_warehouse_distance DOUBLE NOT NULL DEFAULT 0.10 COMMENT 'Trọng số khoảng cách kho (Cost)',
    
    -- Trọng số cho các tiêu chí BENEFIT (tổng weight_benefit phải = 0.5)
    weight_floor_area DOUBLE NOT NULL DEFAULT 0.15 COMMENT 'Trọng số diện tích sàn (Benefit)',
    weight_front_width DOUBLE NOT NULL DEFAULT 0.10 COMMENT 'Trọng số mặt tiền (Benefit)',
    weight_traffic_score DOUBLE NOT NULL DEFAULT 0.15 COMMENT 'Trọng số lưu lượng giao thông (Benefit)',
    weight_population_density DOUBLE NOT NULL DEFAULT 0.10 COMMENT 'Trọng số mật độ dân cư (Benefit)',
    
    -- Metadata
    is_active BOOLEAN DEFAULT FALSE COMMENT 'Cấu hình đang được sử dụng (chỉ 1 record = TRUE)',
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
COMMENT='Bảng cấu hình trọng số chuyên gia cho TOPSIS';

-- ============================================================================
-- 3. POTENTIAL SITE TABLE
-- Bảng chính lưu trữ dữ liệu các địa điểm ứng viên
-- Chứa các tiêu chí đầu vào và kết quả TOPSIS
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
    -- THUỘC TÍNH BỔ SUNG (Có thể dùng cho lọc hoặc phân tích bổ sung)
    -- ========================================================================
    has_parking BOOLEAN DEFAULT FALSE COMMENT 'Có chỗ đỗ xe',
    is_corner_lot BOOLEAN DEFAULT FALSE COMMENT 'Là lô góc (2 mặt tiền)',
    near_school BOOLEAN DEFAULT FALSE COMMENT 'Gần trường học',
    near_market BOOLEAN DEFAULT FALSE COMMENT 'Gần chợ truyền thống',
    
    -- ========================================================================
    -- KẾT QUẢ TOPSIS (Được Python script cập nhật)
    -- ========================================================================
    topsis_score DOUBLE COMMENT 'Điểm TOPSIS (0-1, càng cao càng tốt)',
    rank_position INT COMMENT 'Thứ hạng (1 = tốt nhất)',
    last_analysis_date DATETIME COMMENT 'Thời điểm phân tích TOPSIS gần nhất',
    config_used_id BIGINT COMMENT 'ID cấu hình trọng số được dùng khi phân tích',
    
    -- Metadata
    status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT 'ACTIVE, RENTED, REJECTED',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes TEXT COMMENT 'Ghi chú bổ sung',
    
    FOREIGN KEY (district_id) REFERENCES district(id),
    FOREIGN KEY (config_used_id) REFERENCES expert_criteria_config(id),
    
    INDEX idx_district (district_id),
    INDEX idx_status (status),
    INDEX idx_rank (rank_position),
    INDEX idx_topsis_score (topsis_score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng lưu trữ các địa điểm ứng viên và kết quả phân tích TOPSIS';

-- ============================================================================
-- SAMPLE DATA FOR DISTRICTS
-- ============================================================================
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

-- ============================================================================
-- SAMPLE EXPERT CRITERIA CONFIGS
-- ============================================================================

-- Chiến lược 1: PHỦ SÓNG THỊ TRƯỜNG (Ưu tiên vị trí đắc địa, chấp nhận chi phí cao)
INSERT INTO expert_criteria_config (
    strategy_name, description,
    weight_rent_cost, weight_renovation_cost, weight_competitor_count, weight_warehouse_distance,
    weight_floor_area, weight_front_width, weight_traffic_score, weight_population_density,
    is_active, created_by
) VALUES (
    'Phủ Sóng Thị Trường',
    'Ưu tiên vị trí có lưu lượng cao, mật độ dân cư cao. Chấp nhận giá thuê và cạnh tranh cao.',
    0.08, 0.07, 0.10, 0.05,  -- Cost weights (tổng: 0.30)
    0.12, 0.10, 0.25, 0.23,  -- Benefit weights (tổng: 0.70) - Traffic & Population ưu tiên
    TRUE,
    'Strategy Team'
);

-- Chiến lược 2: TỐI ƯU LỢI NHUẬN (Ưu tiên chi phí thấp, tránh cạnh tranh)
INSERT INTO expert_criteria_config (
    strategy_name, description,
    weight_rent_cost, weight_renovation_cost, weight_competitor_count, weight_warehouse_distance,
    weight_floor_area, weight_front_width, weight_traffic_score, weight_population_density,
    is_active, created_by
) VALUES (
    'Tối Ưu Lợi Nhuận',
    'Ưu tiên chi phí thấp, ít đối thủ cạnh tranh. Chấp nhận traffic thấp hơn một chút.',
    0.25, 0.15, 0.20, 0.10,  -- Cost weights (tổng: 0.70) - Rent & Competitor ưu tiên
    0.10, 0.05, 0.08, 0.07,  -- Benefit weights (tổng: 0.30)
    FALSE,
    'Finance Team'
);

-- Chiến lược 3: CÂN BẰNG (Trọng số cân đối)
INSERT INTO expert_criteria_config (
    strategy_name, description,
    weight_rent_cost, weight_renovation_cost, weight_competitor_count, weight_warehouse_distance,
    weight_floor_area, weight_front_width, weight_traffic_score, weight_population_density,
    is_active, created_by
) VALUES (
    'Cân Bằng Toàn Diện',
    'Cân đối giữa chi phí và lợi ích. Phù hợp cho giai đoạn mở rộng ổn định.',
    0.15, 0.10, 0.12, 0.08,  -- Cost weights (tổng: 0.45)
    0.15, 0.10, 0.15, 0.15,  -- Benefit weights (tổng: 0.55)
    FALSE,
    'Operations Team'
);

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- View: Top 10 địa điểm tốt nhất
CREATE OR REPLACE VIEW vw_top_sites AS
SELECT 
    ps.id,
    ps.site_code,
    ps.address,
    d.name as district_name,
    ps.topsis_score,
    ps.rank_position,
    ps.rent_cost,
    ps.floor_area,
    ps.traffic_score,
    ps.population_density,
    ps.competitor_count,
    ps.status
FROM potential_site ps
JOIN district d ON ps.district_id = d.id
WHERE ps.status = 'ACTIVE' AND ps.topsis_score IS NOT NULL
ORDER BY ps.rank_position ASC
LIMIT 10;

-- View: Thống kê theo quận
CREATE OR REPLACE VIEW vw_district_summary AS
SELECT 
    d.name as district_name,
    COUNT(ps.id) as total_sites,
    AVG(ps.topsis_score) as avg_topsis_score,
    AVG(ps.rent_cost) as avg_rent_cost,
    AVG(ps.floor_area) as avg_floor_area,
    MIN(ps.rank_position) as best_rank
FROM district d
LEFT JOIN potential_site ps ON d.id = ps.district_id AND ps.status = 'ACTIVE'
GROUP BY d.id, d.name
ORDER BY avg_topsis_score DESC;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================