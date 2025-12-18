# ============================================================================
# Makefile for Retail Site DSS
# Provides shortcuts for common Docker and application commands
# ============================================================================

.PHONY: help build up down restart logs clean test generate-data analyze

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Retail Site DSS - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
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
	@echo "$(GREEN)Services started! Backend: http://localhost:8080$(NC)"

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose down

restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	docker-compose restart

restart-backend: ## Restart only backend service
	@echo "$(YELLOW)Restarting backend...$(NC)"
	docker-compose restart backend

restart-mysql: ## Restart only MySQL service
	@echo "$(YELLOW)Restarting MySQL...$(NC)"
	docker-compose restart mysql

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show logs from backend only
	docker-compose logs -f backend

logs-mysql: ## Show logs from MySQL only
	docker-compose logs -f mysql

logs-python: ## Show logs from Python analyzer
	docker-compose logs -f python-analyzer

ps: ## Show running containers
	docker-compose ps

# ============================================================================
# Development Commands
# ============================================================================

shell-backend: ## Open bash shell in backend container
	docker-compose exec backend bash

shell-mysql: ## Open MySQL shell
	docker-compose exec mysql mysql -u root -p

shell-python: ## Open bash shell in Python container
	docker-compose exec python-analyzer bash

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
	docker-compose exec python-analyzer python generate_data.py

analyze: ## Run TOPSIS analysis
	@echo "$(GREEN)Running TOPSIS analysis...$(NC)"
	curl -s http://localhost:8080/api/analysis/run | jq '.'

top-sites: ## Show top 10 recommended sites
	@echo "$(GREEN)Top 10 Recommended Sites:$(NC)"
	curl -s http://localhost:8080/api/analysis/top-sites?limit=10 | jq '.'

statistics: ## Show site statistics
	@echo "$(GREEN)Site Statistics:$(NC)"
	curl -s http://localhost:8080/api/sites/statistics | jq '.'

health: ## Check backend health
	@echo "$(GREEN)Checking backend health...$(NC)"
	curl -s http://localhost:8080/api/analysis/health

districts: ## List all districts
	@echo "$(GREEN)Districts:$(NC)"
	curl -s http://localhost:8080/api/districts | jq '.'

# ============================================================================
# Database Commands
# ============================================================================

db-backup: ## Backup database to file
	@echo "$(GREEN)Backing up database...$(NC)"
	docker-compose exec mysql mysqldump -u root -p retail_dss > database/backup/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup completed!$(NC)"

db-restore: ## Restore database from latest backup (use: make db-restore FILE=backup.sql)
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
	docker-compose exec mysql mysql -u root -p retail_dss < database/init/01-schema.sql
	docker-compose exec mysql mysql -u root -p retail_dss < database/init/02-seed-districts.sql
	docker-compose exec mysql mysql -u root -p retail_dss < database/init/03-seed-configs.sql
	@echo "$(GREEN)Database reset completed!$(NC)"

# ============================================================================
# Test Commands
# ============================================================================

test-backend: ## Run backend tests
	@echo "$(GREEN)Running backend tests...$(NC)"
	cd backend && ./mvnw test

test-all: test-backend ## Run all tests

# ============================================================================
# Full Workflow Commands
# ============================================================================

init: build up ## Initialize project (build and start)
	@echo "$(GREEN)Waiting for services to be ready...$(NC)"
	@sleep 10
	@echo "$(GREEN)Project initialized successfully!$(NC)"
	@echo "$(GREEN)Backend API: http://localhost:8080$(NC)"
	@echo "$(GREEN)Run 'make generate-data' to create sample data$(NC)"

full-setup: init generate-data analyze ## Complete setup with data generation and analysis
	@echo "$(GREEN)Full setup completed!$(NC)"
	@echo "$(GREEN)Check results with: make top-sites$(NC)"

demo: ## Run a complete demo workflow
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN) Retail Site DSS - Demo Workflow$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(GREEN)1. Checking backend health...$(NC)"
	@make health
	@echo ""
	@sleep 2
	@echo "$(GREEN)2. Generating sample data...$(NC)"
	@make generate-data
	@echo ""
	@sleep 2
	@echo "$(GREEN)3. Running TOPSIS analysis...$(NC)"
	@make analyze
	@echo ""
	@sleep 2
	@echo "$(GREEN)4. Showing top 10 sites...$(NC)"
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
	docker-compose logs -f --tail=100 backend

monitor: ## Show resource usage
	docker stats $$(docker-compose ps -q)

# ============================================================================
# Default target
# ============================================================================

.DEFAULT_GOAL := help
