# 🏪 Retail Site Selection Decision Support System (DSS)

Hệ thống hỗ trợ ra quyết định chọn địa điểm mở chuỗi siêu thị mini sử dụng thuật toán MCDM (Multi-Criteria Decision Making).

## 📋 Mục lục

- [Tổng quan](#tổng-quan)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Cài đặt & Chạy](#cài-đặt--chạy)
- [API Documentation](#api-documentation)
- [Mở rộng thuật toán](#mở-rộng-thuật-toán)

## 🎯 Tổng quan

Hệ thống DSS này giúp các doanh nghiệp bán lẻ đưa ra quyết định khoa học khi chọn địa điểm mở cửa hàng mới. Sử dụng các thuật toán MCDM để phân tích đa tiêu chí.

### Thuật toán được hỗ trợ

- ✅ **TOPSIS** - Technique for Order Preference by Similarity to Ideal Solution
- 🚧 **AHP** - Analytic Hierarchy Process (Coming soon)
- 🚧 **ELECTRE** - ELimination Et Choix Traduisant la REalité (Coming soon)
- 🚧 **PROMETHEE** - Preference Ranking Organization METHod (Coming soon)

### Tiêu chí đánh giá

**Cost (Càng thấp càng tốt)**
- 💰 Giá thuê mặt bằng
- 🔧 Chi phí sửa chữa/setup
- 🏢 Số lượng đối thủ cạnh tranh
- 🚚 Khoảng cách đến kho trung tâm

**Benefit (Càng cao càng tốt)**
- 📐 Diện tích sàn kinh doanh
- 🚪 Chiều rộng mặt tiền
- 🚗 Lưu lượng giao thông
- 👥 Mật độ dân cư khu vực

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐
│   Client/API    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      HTTP/REST      ┌──────────────────┐
│  Spring Boot    │ ◄─────────────────► │  Flask MCDM      │
│    Backend      │                      │    Service       │
└────────┬────────┘                      └────────┬─────────┘
         │                                         │
         │            ┌────────────────────────────┘
         │            │
         ▼            ▼
┌─────────────────────────┐
│    MySQL Database       │
└─────────────────────────┘
```

### Thành phần chính

1. **Spring Boot Backend** (Port 8080)
   - REST API gateway
   - Quản lý dữ liệu sites, districts, configurations
   - Gọi Flask MCDM service để thực hiện phân tích

2. **Flask MCDM Service** (Port 5000)
   - Microservice độc lập xử lý các thuật toán MCDM
   - Dễ dàng mở rộng thêm thuật toán mới
   - RESTful API

3. **MySQL Database** (Port 3306)
   - Lưu trữ dữ liệu sites, configurations, results

4. **Adminer** (Port 8081)
   - Web UI để quản lý database

## 🛠️ Công nghệ sử dụng

- **Backend**: Java 17, Spring Boot 3.2
- **MCDM Service**: Python 3.11, Flask, NumPy, Pandas
- **Database**: MySQL 8.0
- **Containerization**: Docker & Docker Compose
- **Build Tool**: Maven 3.9

## 📦 Cài đặt & Chạy

### Quick Start với Docker

```bash
# 1. Clone repository
git clone <repository-url>
cd retail-site-dss

# 2. Cấu hình environment
cp .env.example .env
# Edit .env nếu cần

# 3. Khởi động hệ thống
make init

# 4. Generate dữ liệu mẫu
make generate-data

# 5. Chạy phân tích TOPSIS
make analyze

# 6. Xem kết quả
make top-sites
```

### Demo Workflow

```bash
# Chạy toàn bộ demo workflow tự động
make demo
```

## 📚 API Documentation

### Spring Boot Backend APIs

#### 1. Run MCDM Analysis

```bash
# Run with default TOPSIS algorithm
GET http://localhost:8080/api/analysis/run

# Run with specific algorithm
GET http://localhost:8080/api/analysis/run?algorithm=topsis&configId=1&topN=10

# Run specific algorithm via POST
POST http://localhost:8080/api/analysis/topsis
POST http://localhost:8080/api/analysis/ahp
```

**Response:**
```json
{
  "success": true,
  "algorithm": "topsis",
  "strategy_name": "Phủ Sóng Thị Trường",
  "sites_analyzed": 80,
  "execution_time_seconds": 0.45,
  "timestamp": "2024-01-15T10:30:00",
  "score_statistics": {
    "min": 0.2341,
    "max": 0.8756,
    "mean": 0.5234,
    "std": 0.1432
  },
  "top_sites": [
    {
      "rank": 1,
      "site_code": "HCM-Q1-023",
      "address": "456 Nguyen Trai, Quan 1",
      "score": 0.8756,
      "rent_cost": 45.5,
      "floor_area": 120.0,
      "traffic_score": 9,
      "competitor_count": 3
    }
  ]
}
```

#### 2. Get Supported Algorithms

```bash
GET http://localhost:8080/api/analysis/algorithms
```

#### 3. Get Top Sites

```bash
GET http://localhost:8080/api/analysis/top-sites?limit=10
```

#### 4. Health Check

```bash
GET http://localhost:8080/api/analysis/health
```

### Flask MCDM Service APIs

#### 1. Run Analysis

```bash
POST http://localhost:5000/api/analyze
Content-Type: application/json

{
  "algorithm": "topsis",
  "config_id": 1,
  "top_n": 10
}
```

#### 2. List Algorithms

```bash
GET http://localhost:5000/api/algorithms
```

#### 3. Health Check

```bash
GET http://localhost:5000/api/health
```

## 🔧 Makefile Commands

```bash
# Docker
make build              # Build all images
make up                 # Start all services
make down               # Stop all services
make logs               # View logs
make logs-mcdm          # View MCDM service logs

# Application
make generate-data      # Generate sample data
make analyze            # Run TOPSIS analysis
make analyze-ahp        # Run AHP (when available)
make algorithms         # List supported algorithms
make top-sites          # Show top results
make statistics         # Show statistics

# Health
make health             # Check backend health
make health-mcdm        # Check MCDM service health

# Database
make db-backup          # Backup database
make db-restore         # Restore database
make db-reset           # Reset database

# Development
make shell-backend      # Access backend container
make shell-mcdm         # Access MCDM container
make shell-mysql        # Access MySQL shell

# Testing
make test-backend       # Run backend tests
make test-mcdm          # Run MCDM tests

# Workflows
make init               # Initialize project
make full-setup         # Complete setup
make demo               # Run demo workflow
```

## 🚀 Mở rộng thuật toán mới

Flask MCDM service được thiết kế để dễ dàng thêm thuật toán mới:

### Bước 1: Tạo file thuật toán mới

```python
# mcdm/algorithms/ahp.py

from algorithms.base_algorithm import BaseAlgorithm
import pandas as pd

class AHPAlgorithm(BaseAlgorithm):
    """AHP Algorithm Implementation"""
    
    def __init__(self):
        super().__init__('AHP')
    
    def validate_inputs(self, data, weights, cost_criteria, benefit_criteria):
        # Validation logic
        return True
    
    def analyze(self, data, weights, cost_criteria, benefit_criteria):
        # AHP algorithm implementation
        df = data.copy()
        
        # Your AHP logic here
        # ...
        
        df['ahp_score'] = scores
        df['rank_position'] = ranks
        
        return df
```

### Bước 2: Đăng ký thuật toán

```python
# mcdm/algorithms/base_algorithm.py

class AlgorithmFactory:
    _algorithms = {
        'topsis': TopsisAlgorithm,
        'ahp': AHPAlgorithm,        # Add new algorithm
        'electre': ElectreAlgorithm, # Add new algorithm
    }
```

### Bước 3: Cập nhật config

```python
# mcdm/config.py

class Config:
    SUPPORTED_ALGORITHMS = ['topsis', 'ahp', 'electre', 'promethee']
```

### Bước 4: Test thuật toán mới

```bash
# Rebuild MCDM service
docker-compose build mcdm-service
docker-compose up -d mcdm-service

# Test new algorithm
curl -X POST http://localhost:8080/api/analysis/ahp | jq '.'
```

Hoặc qua Makefile:
```bash
make restart-mcdm
make analyze-ahp
```

## 🔄 Workflow thay đổi chiến lược

```bash
# 1. Connect to database
docker-compose exec mysql mysql -u root -p retail_dss

# 2. Switch strategy
UPDATE expert_criteria_config SET is_active = FALSE WHERE is_active = TRUE;
UPDATE expert_criteria_config SET is_active = TRUE WHERE strategy_name = 'Tối Ưu Lợi Nhuận';

# 3. Re-run analysis
make analyze

# 4. Compare results
make top-sites
```

## 📊 Monitoring

```bash
# View all logs
make watch-logs

# Monitor resources
make monitor

# Check service status
docker-compose ps
```

## 🐛 Troubleshooting

### MCDM Service không kết nối được database

```bash
# Check MCDM service logs
make logs-mcdm

# Check database connection
docker-compose exec mcdm-service python -c "from utils.db_connector import test_connection; print(test_connection())"
```

### Backend không gọi được MCDM service

```bash
# Check MCDM service health
make health-mcdm

# Verify network
docker-compose exec manager curl http://mcdm-service:5000/api/health
```

## 📝 Notes

- Dữ liệu mẫu được generate với logic correlation thực tế
- Flask MCDM service chạy độc lập, dễ scale và deploy riêng biệt
- Hỗ trợ multiple strategies qua bảng `expert_criteria_config`
- Kết quả được cache trong database để reporting

## 🤝 Contributing

Để thêm thuật toán MCDM mới, chỉ cần:
1. Tạo file trong `mcdm/algorithms/`
2. Kế thừa từ `BaseAlgorithm`
3. Implement methods: `validate_inputs()` và `analyze()`
4. Đăng ký trong `AlgorithmFactory`
