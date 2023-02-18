static:
	docker compose exec web python manage.py collectstatic --no-input

collect:
	docker compose exec web python manage.py collectstatic --no-input

reset:
	docker system prune -af --volumes
	docker compose build

bash:
	docker compose exec -it web bash

run:
	docker compose up

test:
	docker compose exec -it web pytest

clean:
	docker system prune -af --volumes

lint:
	black .
	isort --profile black .

initial_data:
	docker compose exec -it web python manage.py loaddata initial_tiers

makemigrations:
	docker compose exec -it web python manage.py makemigrations

migrate:
	docker compose exec -it web python manage.py migrate