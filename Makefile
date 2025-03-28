# Старт базы данных
start-db:
	docker-compose -f infra/dev/docker-compose.dev.yaml up -d postgres

# Остановка базы данных
stop-db:
	docker-compose -f infra/dev/docker-compose.dev.yaml down

run:
	python -m uvicorn main:app --host 0.0.0.0 --port 8000
