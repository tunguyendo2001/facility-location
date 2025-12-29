#!/usr/bin/env python3
"""
============================================================================
TOPSIS Analysis Script for Retail Site Selection
Thuật toán TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
============================================================================
"""

import mysql.connector
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Thay đổi password của bạn
    'database': 'retail_dss',
    'charset': 'utf8mb4'
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_db_connection():
    """Tạo kết nối đến MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✓ Connected to MySQL database successfully")
        return conn
    except mysql.connector.Error as err:
        print(f"✗ Error connecting to MySQL: {err}")
        raise

def load_active_config(conn):
    """
    Load cấu hình trọng số đang active từ database
    Returns: Dictionary chứa các trọng số
    """
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM ExpertCriteriaConfig WHERE is_active = TRUE LIMIT 1"
    cursor.execute(query)
    config = cursor.fetchone()
    cursor.close()
    
    if not config:
        raise Exception("No active configuration found in ExpertCriteriaConfig table")
    
    print(f"\n✓ Loaded active configuration: '{config['strategy_name']}'")
    print(f"  Description: {config['description']}")
    
    return {
        'config_id': config['id'],
        'strategy_name': config['strategy_name'],
        # Cost weights (thuộc tính càng thấp càng tốt)
        'rent_cost': config['weight_rent_cost'],
        'renovation_cost': config['weight_renovation_cost'],
        'competitor_count': config['weight_competitor_count'],
        'warehouse_distance': config['weight_warehouse_distance'],
        # Benefit weights (thuộc tính càng cao càng tốt)
        'floor_area': config['weight_floor_area'],
        'front_width': config['weight_front_width'],
        'traffic_score': config['weight_traffic_score'],
        'population_density': config['weight_population_density']
    }

def load_potential_sites(conn):
    """
    Load dữ liệu các địa điểm ứng viên từ database
    Returns: Pandas DataFrame
    """
    query = """
        SELECT 
            id, site_code, address,
            rent_cost, renovation_cost, competitor_count, distance_to_warehouse,
            floor_area, front_width, traffic_score, population_density
        FROM PotentialSite
        WHERE status = 'ACTIVE'
    """
    df = pd.read_sql(query, conn)
    print(f"\n✓ Loaded {len(df)} potential sites from database")
    return df

# ============================================================================
# TOPSIS ALGORITHM IMPLEMENTATION
# ============================================================================

def normalize_matrix(matrix):
    """
    Bước 1: Chuẩn hóa ma trận quyết định theo phương pháp Vector Normalization
    Formula: r_ij = x_ij / sqrt(sum(x_ij^2))
    """
    norm_matrix = matrix / np.sqrt((matrix ** 2).sum(axis=0))
    return norm_matrix

def apply_weights(norm_matrix, weights):
    """
    Bước 2: Nhân ma trận chuẩn hóa với trọng số
    """
    weighted_matrix = norm_matrix * weights
    return weighted_matrix

def get_ideal_solutions(weighted_matrix, benefit_indices, cost_indices):
    """
    Bước 3: Xác định giải pháp lý tưởng tốt nhất (A+) và tệ nhất (A-)
    
    - Với thuộc tính Benefit: A+ = max, A- = min
    - Với thuộc tính Cost: A+ = min, A- = max
    """
    ideal_best = np.zeros(weighted_matrix.shape[1])
    ideal_worst = np.zeros(weighted_matrix.shape[1])
    
    # Benefit attributes: max là tốt nhất
    ideal_best[benefit_indices] = weighted_matrix[:, benefit_indices].max(axis=0)
    ideal_worst[benefit_indices] = weighted_matrix[:, benefit_indices].min(axis=0)
    
    # Cost attributes: min là tốt nhất
    ideal_best[cost_indices] = weighted_matrix[:, cost_indices].min(axis=0)
    ideal_worst[cost_indices] = weighted_matrix[:, cost_indices].max(axis=0)
    
    return ideal_best, ideal_worst

def calculate_distances(weighted_matrix, ideal_best, ideal_worst):
    """
    Bước 4: Tính khoảng cách Euclidean đến giải pháp lý tưởng
    
    D+ = sqrt(sum((v_ij - A+_j)^2))
    D- = sqrt(sum((v_ij - A-_j)^2))
    """
    dist_to_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
    dist_to_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))
    
    return dist_to_best, dist_to_worst

def calculate_topsis_scores(dist_to_best, dist_to_worst):
    """
    Bước 5: Tính điểm TOPSIS (Relative Closeness)
    
    C_i = D- / (D+ + D-)
    
    Giá trị C_i càng gần 1 thì phương án càng tốt
    """
    scores = dist_to_worst / (dist_to_best + dist_to_worst)
    return scores

def run_topsis_analysis(df, weights_config):
    """
    Hàm chính thực hiện toàn bộ quy trình TOPSIS
    """
    print("\n" + "="*70)
    print("STARTING TOPSIS ANALYSIS")
    print("="*70)
    
    # Chuẩn bị ma trận dữ liệu
    # Thứ tự cột: [rent_cost, renovation_cost, competitor_count, warehouse_distance,
    #              floor_area, front_width, traffic_score, population_density]
    criteria_columns = [
        'rent_cost', 'renovation_cost', 'competitor_count', 'distance_to_warehouse',
        'floor_area', 'front_width', 'traffic_score', 'population_density'
    ]
    
    decision_matrix = df[criteria_columns].values
    print(f"\nDecision Matrix Shape: {decision_matrix.shape}")
    
    # Chuẩn bị vector trọng số
    weights = np.array([
        weights_config['rent_cost'],
        weights_config['renovation_cost'],
        weights_config['competitor_count'],
        weights_config['warehouse_distance'],
        weights_config['floor_area'],
        weights_config['front_width'],
        weights_config['traffic_score'],
        weights_config['population_density']
    ])
    
    print(f"\nWeights Configuration:")
    for i, col in enumerate(criteria_columns):
        print(f"  {col:25s}: {weights[i]:.3f}")
    print(f"  {'TOTAL':25s}: {weights.sum():.3f}")
    
    # Định nghĩa indices cho Cost và Benefit
    cost_indices = [0, 1, 2, 3]      # rent_cost, renovation_cost, competitor_count, warehouse_distance
    benefit_indices = [4, 5, 6, 7]   # floor_area, front_width, traffic_score, population_density
    
    # Bước 1: Chuẩn hóa ma trận
    print("\n[Step 1] Normalizing decision matrix...")
    norm_matrix = normalize_matrix(decision_matrix)
    
    # Bước 2: Nhân với trọng số
    print("[Step 2] Applying weights...")
    weighted_matrix = apply_weights(norm_matrix, weights)
    
    # Bước 3: Tìm giải pháp lý tưởng
    print("[Step 3] Finding ideal solutions...")
    ideal_best, ideal_worst = get_ideal_solutions(weighted_matrix, benefit_indices, cost_indices)
    
    # Bước 4: Tính khoảng cách
    print("[Step 4] Calculating distances to ideal solutions...")
    dist_to_best, dist_to_worst = calculate_distances(weighted_matrix, ideal_best, ideal_worst)
    
    # Bước 5: Tính điểm TOPSIS
    print("[Step 5] Calculating TOPSIS scores...")
    topsis_scores = calculate_topsis_scores(dist_to_best, dist_to_worst)
    
    # Tính rank (thứ hạng)
    ranks = pd.Series(topsis_scores).rank(ascending=False, method='min').astype(int).values
    
    # Thêm kết quả vào DataFrame
    df['topsis_score'] = topsis_scores
    df['rank_position'] = ranks
    
    print(f"\n✓ TOPSIS analysis completed")
    print(f"  Score range: {topsis_scores.min():.4f} - {topsis_scores.max():.4f}")
    print(f"  Mean score: {topsis_scores.mean():.4f}")
    
    return df

def update_database(conn, df, config_id):
    """
    Cập nhật kết quả TOPSIS vào database
    """
    print("\n" + "="*70)
    print("UPDATING DATABASE WITH RESULTS")
    print("="*70)
    
    cursor = conn.cursor()
    update_count = 0
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for _, row in df.iterrows():
        query = """
            UPDATE PotentialSite
            SET topsis_score = %s,
                rank_position = %s,
                last_analysis_date = %s,
                config_used_id = %s
            WHERE id = %s
        """
        values = (
            float(row['topsis_score']),
            int(row['rank_position']),
            current_time,
            config_id,
            int(row['id'])
        )
        
        cursor.execute(query, values)
        update_count += 1
    
    conn.commit()
    cursor.close()
    
    print(f"✓ Updated {update_count} records in database")

def print_top_results(df, top_n=10):
    """
    In ra top N địa điểm tốt nhất
    """
    print("\n" + "="*70)
    print(f"TOP {top_n} RECOMMENDED SITES")
    print("="*70)
    
    top_sites = df.nsmallest(top_n, 'rank_position')
    
    for idx, row in top_sites.iterrows():
        print(f"\nRank #{int(row['rank_position'])}: {row['site_code']}")
        print(f"  Address: {row['address']}")
        print(f"  TOPSIS Score: {row['topsis_score']:.4f}")
        print(f"  Key Metrics:")
        print(f"    - Rent Cost: {row['rent_cost']:.1f}M VND")
        print(f"    - Floor Area: {row['floor_area']:.0f} m²")
        print(f"    - Traffic Score: {row['traffic_score']}/10")
        print(f"    - Competitors: {row['competitor_count']}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Hàm main thực hiện toàn bộ quy trình
    """
    try:
        print("\n" + "="*70)
        print("RETAIL SITE SELECTION DSS - TOPSIS ANALYSIS")
        print("="*70)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Kết nối database
        conn = get_db_connection()
        
        # 2. Load cấu hình trọng số
        weights_config = load_active_config(conn)
        
        # 3. Load dữ liệu địa điểm
        df = load_potential_sites(conn)
        
        if len(df) == 0:
            print("\n✗ No sites found to analyze. Exiting.")
            return
        
        # 4. Chạy phân tích TOPSIS
        df_results = run_topsis_analysis(df, weights_config)
        
        # 5. Cập nhật kết quả vào database
        update_database(conn, df_results, weights_config['config_id'])
        
        # 6. In kết quả top sites
        print_top_results(df_results, top_n=10)
        
        # Đóng kết nối
        conn.close()
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
