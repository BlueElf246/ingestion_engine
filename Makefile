install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

build-image:
	docker build -t ingestion_project:latest .

docker-up:
	docker-compose up --build

.PHONY: install run docker-build docker-up
