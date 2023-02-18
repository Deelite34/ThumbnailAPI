# ThumbnailAPI
Project that allows user to upload images through REST API to get thumbnails, depending on account tier, and view them on their own pages. 
It's also possible to create time limited thumbnails.  

## Features
- Uses django, django rest framework, docker, docker-compose, postgresql, configured nginx server with gunicorn
- Upload image to have server generate various-sized thumbnails, or a single time-limited thumbnail, viewable under their own urls
- Media and static files served by nginx
- Tests with pytest
- Authorization with djoser using auth token or JWT token

## Authorization
To use API, either django token or JWT token needs to be used.  
To get one of token, send POST request with `username` and `password` parameters to `/api/v1/auth/token/login/` or `/api/v1/auth/jwt/create/` endpoint.
Include acquired token using Authorization header.

## Installation and configuration

Create '.env' file using `template.env` file  
`docker compose up`  
`docker compose exec web python manage.py migrate`  
`docker compose exec web python manage.py collectstatic --noinput`  
`docker compose exec web python manage.py loaddata initial_tiers` Load fixture with 3 account tiers. More can be created manually.  
  
Website will be available under url `localhost:1337`  
`docker compose exec web python manage.py createsuperuser` 
Log into the admin panel http://localhost:1337/admin/API/apiuser/  
Assign one of the Account Types to created superuser account, or create new account and change its account type.  
  
Get auth or JWT token and include it in future request headers  
API documentation can be found under `/api/v1/schema/swagger-ui/`  

## Tests
To run tests, execute command `docker compose exec -it web pytest`

## Endpoint documentation
Documentation can be found after application installation under `/api/v1/schema/swagger-ui/` address.
