.PHONY: create-keys build stop

create-keys:
	mkdir certs
	openssl genrsa -out certs/jwt-private.pem 2048
	openssl rsa -in certs/jwt-private.pem -outform PEM -pubout -out certs/jwt-public.pem

build:
	docker-compose up -d --build

stop:
	docker-compose down

create-env:
	touch .dev.env
	