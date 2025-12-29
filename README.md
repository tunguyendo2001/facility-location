# 🏪 Retail Site Selection Decision Support System (DSS)

Hệ thống hỗ trợ ra quyết định chọn địa điểm mở chuỗi siêu thị mini sử dụng thuật toán TOPSIS (Technique for Order Preference by Similarity to Ideal Solution).

## 📋 Mục lục

- [Tổng quan](#tổng-quan)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Cài đặt & Chạy](#cài-đặt--chạy)
- [API Documentation](#api-documentation)
- [Docker Deployment](#docker-deployment)

## 🎯 Tổng quan

Hệ thống DSS này giúp các doanh nghiệp bán lẻ đưa ra quyết định khoa học khi chọn địa điểm mở cửa hàng mới. Sử dụng thuật toán TOPSIS để phân tích đa tiêu chí, hệ thống xem xét các yếu tố:

### Tiêu chí Cost (Càng thấp càng tốt)
- 💰 Giá thuê mặt bằng
- 🔧 Chi phí sửa chữa/setup
- 🏢 Số lượng đối thủ cạnh tranh
- 🚚 Khoảng cách đến kho trung tâm

### Tiêu chí Benefit (Càng cao càng tốt)
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
┌─────────────────┐
│  Spring Boot    │ ◄─── Python TOPSIS Engine
│    Backend      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MySQL Database │
└─────────────────┘
```

## 🛠️ Công nghệ sử dụng

- **Backend**: Java 17, Spring Boot 3.2
- **Database**: MySQL 8.0
- **Analysis Engine**: Python 3.11, NumPy, Pandas
- **Containerization**: Docker & Docker Compose
- **Build Tool**: Maven 3.9

## 📦 Cài đặt & Chạy

### Option 1: Chạy với Docker (Khuyến nghị)

#### Bước 1: Clone repository
```bash
git clone <repository-url>
cd retail-site-dss
```

#### Bước 2: Cấu hình environment variables
```bash
cp .env.example .env
# Edit .env file với các giá trị phù hợp
```

#### Bước 3: Build và chạy với Docker Compose
```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Bước 4: Generate dữ liệu mẫu
```bash
# Chạy data generator script
docker-compose exec python-analyzer python generate_data.py
```

#### Bước 5: Chạy phân tích TOPSIS
```bash
# Option A: Gọi API từ Spring Boot
curl http://localhost:8080/api/analysis/run

# Option B: Chạy trực tiếp Python script
docker-compose exec python-analyzer python topsis.py
```

#### Bước 6: Xem kết quả
```bash
# Get top 10 sites
curl http://localhost:8080/api/analysis/top-sites?limit=10

# Get statistics
curl http://localhost:8080/api/sites/statistics
```

### Option 2: Chạy Local (Development)

#### Prerequisites
- Java 17+
- Maven 3.6+
- MySQL 8.0+
- Python 3.11+

#### Bước 1: Setup database
```bash
mysql -u root -p < database/init/01-schema.sql
mysql -u root -p retail_dss < database/init/02-seed-districts.sql
mysql -u root -p retail_dss < database/init/03-seed-configs.sql
```

#### Bước 2: Install Python dependencies
```bash
cd mcdm
pip install -r requirements.txt
```

#### Bước 3: Generate dữ liệu mẫu
```bash
python generate_data.py
```

#### Bước 4: Run Spring Boot application
```bash
cd backend
./mvnw spring-boot:run -Dspring-boot.run.profiles=dev
```

#### Bước 5: Test API
```bash
curl http://localhost:8080/api/analysis/health
curl http://localhost:8080/api/analysis/run
```

## 📚 API Documentation

### Health Check
```
GET /api/analysis/health
Response: "Retail DSS Analysis Service is running"
```

### Run TOPSIS Analysis
```
GET /api/analysis/run

Response:
{
  "success": true,
  "message": "TOPSIS analysis completed successfully",
  "timestamp": "2024-01-15T10:30:00",
  "sitesAnalyzed": 80,
  "pythonOutput": "..."
}
```

### Get Top Sites
```
GET /api/analysis/top-sites?limit=10

Response:
[
  {
    "id": 1,
    "siteCode": "HCM-Q1-001",
    "address": "123 Nguyen Trai, Quan 1",
    "districtName": "Quan 1",
    "topsisScore": 0.8523,
    "rankPosition": 1,
    "rentCost": 45.5,
    "floorArea": 120.0,
    "trafficScore": 9,
    "competitorCount": 3
  },
  ...
]
```

### Get All Districts
```
GET /api/districts

Response:
[
  {
    "id": 1,
    "name": "Quan 1",
    "xCoordinate": 106.6980,
    "yCoordinate": 10.7758,
    "populationDensity": 38000.0
  },
  ...
]
```

### Get Site Statistics
```
GET /api/sites/statistics

Response:
{
  "totalSites": 80,
  "activeSites": 80,
  "analyzedSites": 80,
  "averageTopsisScore": 0.5234,
  "averageRentCost": 28.5
}
```

## 🐳 Docker Commands

### Quản lý containers
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend
docker-compose logs -f mysql

# Execute command in container
docker-compose exec backend bash
docker-compose exec mysql mysql -u root -p
```

### Rebuild after code changes
```bash
# Rebuild backend only
docker-compose build backend
docker-compose up -d backend

# Rebuild all
docker-compose down
docker-compose build
docker-compose up -d
```

### Database operations
```bash
# Backup database
docker-compose exec mysql mysqldump -u root -p retail_dss > backup.sql

# Restore database
docker-compose exec -T mysql mysql -u root -p retail_dss < backup.sql

# Access MySQL shell
docker-compose exec mysql mysql -u root -p retail_dss
```

## 🔧 Troubleshooting

### Backend không kết nối được database
```bash
# Check MySQL health
docker-compose ps
docker-compose logs mysql

# Verify connection
docker-compose exec mysql mysql -u retailuser -p -e "SHOW DATABASES;"
```

### Python script lỗi
```bash
# Check Python container logs
docker-compose logs python-analyzer

# Test manually
docker-compose exec python-analyzer python topsis.py
```

### Port conflicts
```bash
# Check ports in use
lsof -i :8080
lsof -i :3306

# Change ports in .env file
BACKEND_PORT=8081
MYSQL_PORT=3307
```

## 📊 Thay đổi chiến lược phân tích

Để thay đổi chiến lược (trọng số) phân tích:

```sql
-- Connect to database
docker-compose exec mysql mysql -u root -p retail_dss

-- Deactivate current strategy
UPDATE ExpertCriteriaConfig SET is_active = FALSE WHERE is_active = TRUE;

-- Activate new strategy (ví dụ: "Tối Ưu Lợi Nhuận")
UPDATE ExpertCriteriaConfig 
SET is_active = TRUE 
WHERE strategy_name = 'Tối Ưu Lợi Nhuận';

-- Verify
SELECT id, strategy_name, is_active FROM ExpertCriteriaConfig;
```

Sau đó chạy lại phân tích:
```bash
curl http://localhost:8080/api/analysis/run
```

## 📝 Notes

- Dữ liệu hiện tại là fake data với logic correlation thực tế
- Database schema được tối ưu cho thuật toán TOPSIS
- Hệ thống hỗ trợ multiple strategies thông qua bảng ExpertCriteriaConfig
- Kết quả TOPSIS được lưu vào database để tracking và reporting

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Team Name
