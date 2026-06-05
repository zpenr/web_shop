.PHONY: create-keys build stop format lint mypy ci

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