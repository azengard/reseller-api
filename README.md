### About

DRF API to manage reseller's purchase and cashback

### Version
1.0

### How set up and run the project

1. Configure project.
```console
git@github.com:azengard/reseller-api.git
cd reseller-api
cp .env-sample .env
```

2. Run Project using Docker-Compose (The Fastest Way)
* Develop
```console
docker-compose up
```

* Production
```console
docker-compose -f docker-compose-prod.yml up
```

After the containers are up and running you can access the api at [http://localhost:8000/api/](http://localhost:8000/api/)

You can also use the application with the 
[OpenAPI documentation](http://localhost:8000/api/docs/)


3. Run project locally
```console
python -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install --dev
```

**Important!** make sure postgres container are up.
```console
python manage.py migrate
python manage.py runserver
```

4. Run project tests
**Important!** make sure postgres container are up.
```console
pytest
```

### Docker services

####Backend
* Django application, serve de API and communicate with database.
```console
docker-compose up backend
```

####NGINX
* Used to serve the Swagger application and redirect requests to Backend.
```console
docker-compose up nginx
```

####Postgres
* A robust and secure database.
```console
docker-compose up postgres
```

### API
**Basepath: http://localhost:8000/api/**
