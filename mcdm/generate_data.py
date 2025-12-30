"""
============================================================================
Data Generator Script for Retail Site Selection DSS
Tạo dữ liệu mẫu có tính logic thực tế cho hệ thống
============================================================================
"""

import mysql.connector
import numpy as np
import random
import os
from datetime import datetime
from pathlib import Path

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

def load_env():
    """Load environment variables from ../.env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes and whitespace
                    value = value.strip().strip("\"").strip("'")
                    os.environ[key.strip()] = value

# Load environment variables
load_env()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'mysql'),
    'user': os.getenv('MYSQL_USER', 'retailuser'),
    'password': os.getenv('MYSQL_PASSWORD', 'retailpass'),
    'database': os.getenv('MYSQL_DATABASE', 'retail_dss'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'charset': 'utf8mb4'
}

# ============================================================================
# DATA GENERATION PARAMETERS
# ============================================================================

# Danh sách quận (lấy từ database)
DISTRICTS = []

# Tên đường phổ biến ở TP.HCM
STREET_NAMES = [
    'Nguyễn Trãi', 'Lê Lai', 'Hai Bà Trưng', 'Điện Biên Phủ', 'Võ Văn Tần',
    'Trần Hưng Đạo', 'Nam Kỳ Khởi Nghĩa', 'Phạm Ngũ Lão', 'Cách Mạng Tháng 8',
    'Nguyễn Thị Minh Khai', 'Lê Thánh Tôn', 'Pasteur', 'Alexandre de Rhodes',
    'Võ Thị Sáu', 'Nguyễn Đình Chiểu', 'Nguyễn Văn Cừ', 'Xô Viết Nghệ Tĩnh',
    'Hoàng Văn Thụ', 'Lý Thường Kiệt', 'Phan Đăng Lưu'
]

# ============================================================================
# CORRELATION LOGIC
# ============================================================================
"""
Logic tương quan thực tế:
1. Nếu population_density cao và traffic_score cao 
   -> rent_cost cao, competitor_count cao
   -> Đây là khu vực đắc địa, cạnh tranh khốc liệt

2. Nếu distance_to_warehouse xa
   -> rent_cost thấp hơn (khu ngoại thành)
   -> population_density thấp hơn

3. Nếu floor_area lớn
   -> rent_cost cao (tỷ lệ thuận)

4. Nếu is_corner_lot = True hoặc has_parking = True
   -> rent_cost cao hơn 10-20%

5. Nếu near_school = True
   -> traffic_score cao hơn, population_density cao hơn
"""

def generate_correlated_site_data(district, base_population_density):
    """
    Tạo dữ liệu một địa điểm có tính correlation logic
    """
    # Bước 1: Tạo các yếu tố ngẫu nhiên cơ bản
    base_traffic = random.randint(3, 10)
    distance_to_warehouse = round(random.uniform(1.0, 25.0), 2)
    
    # Bước 2: Điều chỉnh population_density dựa trên khoảng cách kho
    # Càng xa kho (ngoại thành) -> mật độ dân cư càng thấp
    distance_factor = max(0.4, 1 - (distance_to_warehouse / 40))
    population_density = round(base_population_density * distance_factor * random.uniform(0.8, 1.2), 2)
    
    # Bước 3: Traffic score tương quan với population density
    if population_density > 25000:
        traffic_score = random.randint(7, 10)  # Khu đông người -> traffic cao
    elif population_density > 15000:
        traffic_score = random.randint(5, 8)
    else:
        traffic_score = random.randint(3, 6)   # Khu thưa -> traffic thấp
    
    # Bước 4: Diện tích và mặt tiền
    floor_area = round(random.uniform(40, 200), 2)
    front_width = round(random.uniform(4, 15), 2)
    
    # Bước 5: Thuộc tính boolean
    is_corner_lot = random.choice([True, False]) if random.random() > 0.7 else False
    has_parking = random.choice([True, False]) if random.random() > 0.6 else False
    near_school = random.choice([True, False]) if random.random() > 0.5 else False
    near_market = random.choice([True, False]) if random.random() > 0.4 else False
    
    # Bước 6: Tính rent_cost dựa trên nhiều yếu tố
    base_rent = 15  # Triệu VND cơ bản
    
    # 6.1: Điều chỉnh theo population_density và traffic
    location_quality = (population_density / 30000) * 0.6 + (traffic_score / 10) * 0.4
    rent_multiplier = 1 + location_quality * 1.5  # Có thể tăng tới 2.5x
    
    # 6.2: Điều chỉnh theo diện tích (diện tích lớn -> giá cao)
    area_multiplier = 1 + (floor_area / 200) * 0.5
    
    # 6.3: Điều chỉnh theo khoảng cách kho (xa kho -> rẻ hơn)
    distance_multiplier = max(0.6, 1 - (distance_to_warehouse / 50))
    
    # 6.4: Bonus cho corner lot và parking
    bonus_multiplier = 1.0
    if is_corner_lot:
        bonus_multiplier += 0.15
    if has_parking:
        bonus_multiplier += 0.10
    
    rent_cost = round(base_rent * rent_multiplier * area_multiplier * distance_multiplier * bonus_multiplier, 2)
    
    # Bước 7: Renovation cost (tương quan với diện tích)
    renovation_cost = round(floor_area * random.uniform(0.8, 2.0), 2)
    
    # Bước 8: Competitor count (tương quan với location quality)
    if population_density > 25000 and traffic_score >= 7:
        competitor_count = random.randint(5, 15)  # Khu đắc địa -> nhiều đối thủ
    elif population_density > 15000:
        competitor_count = random.randint(2, 7)
    else:
        competitor_count = random.randint(0, 3)   # Khu ít người -> ít đối thủ
    
    # Nếu gần trường học -> tăng competitor
    if near_school:
        competitor_count = min(15, competitor_count + random.randint(1, 3))
    
    return {
        'district_id': district['id'],
        'address': f"{random.randint(1, 999)} {random.choice(STREET_NAMES)}, {district['name']}",
        'x_coordinate': district['x_coordinate'] + random.uniform(-0.02, 0.02),
        'y_coordinate': district['y_coordinate'] + random.uniform(-0.02, 0.02),
        # Cost criteria
        'rent_cost': rent_cost,
        'renovation_cost': renovation_cost,
        'competitor_count': competitor_count,
        'distance_to_warehouse': distance_to_warehouse,
        # Benefit criteria
        'floor_area': floor_area,
        'front_width': front_width,
        'traffic_score': traffic_score,
        'population_density': population_density,
        # Boolean attributes
        'has_parking': has_parking,
        'is_corner_lot': is_corner_lot,
        'near_school': near_school,
        'near_market': near_market,
        'status': 'ACTIVE'
    }

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def get_db_connection():
    """Tạo kết nối đến MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✓ Connected to MySQL database")
        return conn
    except mysql.connector.Error as err:
        print(f"✗ Error: {err}")
        exit(1)

def load_districts(conn):
    """Load danh sách quận từ database"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM district")
    districts = cursor.fetchall()
    cursor.close()
    print(f"✓ Loaded {len(districts)} districts")
    return districts

def clear_existing_sites(conn):
    """Xóa dữ liệu cũ trong bảng potential_site"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM potential_site")
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    print(f"✓ Cleared {deleted} existing records from potential_site")

def insert_potential_site(conn, site_data, site_number):
    """Insert một địa điểm vào database"""
    cursor = conn.cursor()
    
    # Generate site_code
    district_name_short = site_data['address'].split(',')[-1].strip().replace('Quận ', 'Q')
    site_code = f"HCM-{district_name_short}-{site_number:03d}"
    
    query = """
        INSERT INTO potential_site (
            site_code, address, district_id, x_coordinate, y_coordinate,
            rent_cost, renovation_cost, competitor_count, distance_to_warehouse,
            floor_area, front_width, traffic_score, population_density,
            has_parking, is_corner_lot, near_school, near_market, status
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """
    
    values = (
        site_code,
        site_data['address'],
        site_data['district_id'],
        site_data['x_coordinate'],
        site_data['y_coordinate'],
        site_data['rent_cost'],
        site_data['renovation_cost'],
        site_data['competitor_count'],
        site_data['distance_to_warehouse'],
        site_data['floor_area'],
        site_data['front_width'],
        site_data['traffic_score'],
        site_data['population_density'],
        site_data['has_parking'],
        site_data['is_corner_lot'],
        site_data['near_school'],
        site_data['near_market'],
        site_data['status']
    )
    
    cursor.execute(query, values)
    conn.commit()
    cursor.close()

# ============================================================================
# MAIN GENERATION PROCESS
# ============================================================================

def main():
    """
    Hàm main tạo dữ liệu mẫu
    """
    print("\n" + "="*70)
    print("RETAIL SITE SELECTION DSS - DATA GENERATOR")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cấu hình số lượng sites cần tạo
    NUM_SITES_TO_GENERATE = 80
    
    try:
        # 1. Kết nối database
        conn = get_db_connection()
        
        # 2. Load districts
        districts = load_districts(conn)
        
        # 3. Xóa dữ liệu cũ (tùy chọn)
        print("\nClearing existing data...")
        clear_existing_sites(conn)
        
        # 4. Generate và insert sites
        print(f"\nGenerating {NUM_SITES_TO_GENERATE} potential sites...")
        
        for i in range(NUM_SITES_TO_GENERATE):
            # Chọn ngẫu nhiên một quận
            district = random.choice(districts)
            
            # Tạo dữ liệu site với correlation logic
            site_data = generate_correlated_site_data(
                district, 
                district['population_density']
            )
            
            # Insert vào database
            insert_potential_site(conn, site_data, i + 1)
            
            if (i + 1) % 10 == 0:
                print(f"  Generated {i + 1}/{NUM_SITES_TO_GENERATE} sites...")
        
        print(f"\n✓ Successfully generated {NUM_SITES_TO_GENERATE} potential sites")
        
        # 5. Thống kê
        print("\n" + "="*70)
        print("DATA STATISTICS")
        print("="*70)
        
        cursor = conn.cursor(dictionary=True)
        
        # Count by district
        cursor.execute("""
            SELECT d.name, COUNT(ps.id) as count
            FROM district d
            LEFT JOIN potential_site ps ON d.id = ps.district_id
            GROUP BY d.id, d.name
            ORDER BY count DESC
        """)
        print("\nSites by district:")
        for row in cursor.fetchall():
            print(f"  {row['name']:20s}: {row['count']:3d} sites")
        
        # Statistics
        cursor.execute("""
            SELECT 
                MIN(rent_cost) as min_rent, MAX(rent_cost) as max_rent, AVG(rent_cost) as avg_rent,
                MIN(floor_area) as min_area, MAX(floor_area) as max_area, AVG(floor_area) as avg_area,
                MIN(competitor_count) as min_comp, MAX(competitor_count) as max_comp, AVG(competitor_count) as avg_comp,
                MIN(traffic_score) as min_traffic, MAX(traffic_score) as max_traffic, AVG(traffic_score) as avg_traffic
            FROM potential_site
        """)
        stats = cursor.fetchone()
        
        print("\nCriteria Statistics:")
        print(f"  Rent Cost       : {stats['min_rent']:.1f} - {stats['max_rent']:.1f} (avg: {stats['avg_rent']:.1f}) M VND")
        print(f"  Floor Area      : {stats['min_area']:.1f} - {stats['max_area']:.1f} (avg: {stats['avg_area']:.1f}) m²")
        print(f"  Competitors     : {stats['min_comp']} - {stats['max_comp']} (avg: {stats['avg_comp']:.1f})")
        print(f"  Traffic Score   : {stats['min_traffic']} - {stats['max_traffic']} (avg: {stats['avg_traffic']:.1f})")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("DATA GENERATION COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nYou can now run the TOPSIS analysis script.")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()