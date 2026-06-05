.PHONY: create-keys build stop format lint mypy ci install test coverage clean up logs publish-lib help install-lib run create-env

DB_URL ?= sqlite:///database.db
TEST_DB_URL ?= sqlite:///test.db
TESTING ?= true
ALGORITM ?= RS256
ACCESS_TOKEN_EXP_MIN ?= 120
ENV_FILE ?= .dev.env

create-keys:
	mkdir certs
	openssl genrsa -out certs/jwt-private.pem 2048
	openssl rsa -in certs/jwt-private.pem -outform PEM -pubout -out certs/jwt-public.pem

build:
	docker-compose up -d --build

stop:
	docker-compose down

create-env:
	@echo "Создание $(ENV_FILE)..."
	@echo "db_url=$(DB_URL)" > $(ENV_FILE)
	@echo "test_db_url=$(TEST_DB_URL)" >> $(ENV_FILE)
	@echo "testing=$(TESTING)" >> $(ENV_FILE)
	@echo "algoritm=$(ALGORITM)" >> $(ENV_FILE)
	@echo "access_token_exp_min=$(ACCESS_TOKEN_EXP_MIN)" >> $(ENV_FILE)
	@echo "Файл $(ENV_FILE) готов."
	
run:
	uvicorn src.api.app.main:app

format:
	pip install black
	black src/api

lint:
	pip install flake8
	flake8 src/api

mypy:
	pip install mypy
	mypy src/api

ci: format mypy lint 

install:
	python3 -m pip install --upgrade pip
	python3 -m pip install -e .
	python3 -m pip install pytest pytest-cov flake8 black isort mypy sphinx
	make install-lib

install-lib:
	cd src/receipt-pdf-generator && python3 -m pip install -e .

test:
	pytest src/api/tests -v

coverage:
	pytest src/api/tests --cov=src/api/app --cov-report=html --cov-report=term

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true

up:
	docker compose up -d

logs:
	docker compose logs -f