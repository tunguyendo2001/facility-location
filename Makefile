# ============================================================================
# Makefile for Retail Site DSS (Updated with MCDM Service)
# ============================================================================

.PHONY: help build up down restart logs clean test analyze

GREEN  := \033[0;32m
YELLOW := \033[0;33m
BLUE   := \033[0;34m
NC     := \033[0m

help: ## Show this help message
	@echo "$(GREEN)Retail Site DSS - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-25s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================================================
# Docker Commands
# ============================================================================

build: ## Build all Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose build

up: ## Start all services
	@echo "$(GREEN)Starting all services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started!$(NC)"
	@echo "$(BLUE)Backend API:     http://localhost:8080$(NC)"
	@echo "$(BLUE)MCDM Service:    http://localhost:5000$(NC)"
	@echo "$(BLUE)Adminer:         http://localhost:8081$(NC)"

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose down

restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	docker-compose restart

restart-backend: ## Restart only backend service
	@echo "$(YELLOW)Restarting backend...$(NC)"
	docker-compose restart manager

restart-mcdm: ## Restart only MCDM service
	@echo "$(YELLOW)Restarting MCDM service...$(NC)"
	docker-compose restart mcdm-service

restart-mysql: ## Restart only MySQL service
	@echo "$(YELLOW)Restarting MySQL...$(NC)"
	docker-compose restart mysql

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show logs from backend only
	docker-compose logs -f manager

logs-mcdm: ## Show logs from MCDM service
	docker-compose logs -f mcdm-service

logs-mysql: ## Show logs from MySQL only
	docker-compose logs -f mysql

ps: ## Show running containers
	docker-compose ps

# ============================================================================
# Development Commands
# ============================================================================

shell-backend: ## Open bash shell in backend container
	docker-compose exec manager bash

shell-mcdm: ## Open bash shell in MCDM service container
	docker-compose exec mcdm-service bash

shell-mysql: ## Open MySQL shell
	docker-compose exec mysql mysql -u root -p

clean: ## Remove all containers, volumes, and images
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	docker-compose down -v --remove-orphans
	docker-compose rm -f

clean-build: clean build ## Clean and rebuild everything
	@echo "$(GREEN)Clean build completed!$(NC)"

# ============================================================================
# Application Commands
# ============================================================================

generate-data: ## Generate sample data (80 sites)
	@echo "$(GREEN)Generating sample data...$(NC)"
	docker-compose exec mcdm-service python generate_data.py

analyze: ## Run TOPSIS analysis (default algorithm)
	@echo "$(GREEN)Running TOPSIS analysis...$(NC)"
	@curl -s http://localhost:8080/api/analysis/run | jq '.'

analyze-topsis: ## Run TOPSIS analysis explicitly
	@echo "$(GREEN)Running TOPSIS analysis...$(NC)"
	@curl -s -X POST http://localhost:8080/api/analysis/topsis | jq '.'

analyze-ahp: ## Run AHP analysis (when implemented)
	@echo "$(GREEN)Running AHP analysis...$(NC)"
	@curl -s -X POST http://localhost:8080/api/analysis/ahp | jq '.'

algorithms: ## List all supported MCDM algorithms
	@echo "$(GREEN)Supported MCDM Algorithms:$(NC)"
	@curl -s http://localhost:8080/api/analysis/algorithms | jq '.'

top-sites: ## Show top 10 recommended sites
	@echo "$(GREEN)Top 10 Recommended Sites:$(NC)"
	@curl -s http://localhost:8080/api/analysis/top-sites?limit=10 | jq '.'

statistics: ## Show site statistics
	@echo "$(GREEN)Site Statistics:$(NC)"
	@curl -s http://localhost:8080/api/sites/statistics | jq '.'

health: ## Check backend health
	@echo "$(GREEN)Checking backend health...$(NC)"
	@curl -s http://localhost:8080/api/analysis/health | jq '.'

health-mcdm: ## Check MCDM service health
	@echo "$(GREEN)Checking MCDM service health...$(NC)"
	@curl -s http://localhost:5000/api/health | jq '.'

districts: ## List all districts
	@echo "$(GREEN)Districts:$(NC)"
	@curl -s http://localhost:8080/api/districts | jq '.'

# ============================================================================
# Database Commands
# ============================================================================

db-backup: ## Backup database to file
	@echo "$(GREEN)Backing up database...$(NC)"
	docker-compose exec mysql mysqldump -u root -p retail_dss > database/backup/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup completed!$(NC)"

db-restore: ## Restore database from backup (use: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)Usage: make db-restore FILE=backup.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring database from $(FILE)...$(NC)"
	docker-compose exec -T mysql mysql -u root -p retail_dss < $(FILE)
	@echo "$(GREEN)Restore completed!$(NC)"

db-reset: ## Reset database (drop and recreate)
	@echo "$(YELLOW)Resetting database...$(NC)"
	docker-compose exec mysql mysql -u root -p -e "DROP DATABASE IF EXISTS retail_dss; CREATE DATABASE retail_dss;"
	docker-compose exec mysql mysql -u root -p retail_dss < mysql/init/01-schema.sql
	@echo "$(GREEN)Database reset completed!$(NC)"

# ============================================================================
# Test Commands
# ============================================================================

test-backend: ## Run backend tests
	@echo "$(GREEN)Running backend tests...$(NC)"
	cd manager && ./mvnw test

test-mcdm: ## Run MCDM service tests
	@echo "$(GREEN)Running MCDM service tests...$(NC)"
	docker-compose exec mcdm-service pytest

test-all: test-backend test-mcdm ## Run all tests

# ============================================================================
# Full Workflow Commands
# ============================================================================

init: build up ## Initialize project (build and start)
	@echo "$(GREEN)Waiting for services to be ready...$(NC)"
	@sleep 15
	@echo "$(GREEN)Project initialized successfully!$(NC)"
	@echo "$(BLUE)Backend API:     http://localhost:8080$(NC)"
	@echo "$(BLUE)MCDM Service:    http://localhost:5000$(NC)"
	@echo "$(BLUE)Adminer:         http://localhost:8081$(NC)"
	@echo "$(GREEN)Run 'make generate-data' to create sample data$(NC)"

full-setup: init generate-data analyze ## Complete setup with data and analysis
	@echo "$(GREEN)Full setup completed!$(NC)"
	@echo "$(GREEN)Check results with: make top-sites$(NC)"

demo: ## Run a complete demo workflow
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN) Retail Site DSS - Demo Workflow$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(GREEN)1. Checking services health...$(NC)"
	@make health
	@make health-mcdm
	@echo ""
	@sleep 2
	@echo "$(GREEN)2. Listing supported algorithms...$(NC)"
	@make algorithms
	@echo ""
	@sleep 2
	@echo "$(GREEN)3. Generating sample data...$(NC)"
	@make generate-data
	@echo ""
	@sleep 2
	@echo "$(GREEN)4. Running TOPSIS analysis...$(NC)"
	@make analyze
	@echo ""
	@sleep 2
	@echo "$(GREEN)5. Showing top 10 sites...$(NC)"
	@make top-sites
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN) Demo completed successfully!$(NC)"
	@echo "$(GREEN)========================================$(NC)"

# ============================================================================
# Monitoring Commands
# ============================================================================

watch-logs: ## Watch logs in real-time (all services)
	docker-compose logs -f --tail=100

watch-backend: ## Watch backend logs in real-time
	docker-compose logs -f --tail=100 manager

watch-mcdm: ## Watch MCDM service logs in real-time
	docker-compose logs -f --tail=100 mcdm-service

monitor: ## Show resource usage
	docker stats $$(docker-compose ps -q)

# ============================================================================
# Default target
# ============================================================================

.DEFAULT_GOAL := help
