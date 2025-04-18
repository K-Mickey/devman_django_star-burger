up:
	docker compose -f docker-compose.prod.yaml up -d --build

down:
	docker compose -f docker-compose.prod.yaml down

logs:
	docker compose -f docker-compose.prod.yaml logs

migrate:
	docker compose -f docker-compose.prod.yaml exec django python manage.py migrate
