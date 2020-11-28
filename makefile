rebuild:
	docker-compose build --no-cache backend

up:
	docker-compose up

log-backend:
	docker-compose logs --follow backend | ccze -m ansi