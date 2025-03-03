dependencies:
	python3 -m pip install --upgrade pip && pip install -r requirements.txt

migrations:
	python3 manage.py makemigrations && python manage.py migrate

run:
	python3 manage.py runserver

docker-run:
	docker-compose up -d --build && docker-compose exec web python manage.py makemigrations && docker-compose exec web python manage.py migrate

docker-set-webhook:
	docker-compose exec web python manage.py set_webhook