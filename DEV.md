
# Dev locally

Here we expose how to get started when you want to dev locally.

## Prepare

### Prerequisites

* pyenv installed

### Prepare your virtualenv
```
cd infoscience_exports/
pyenv install 3.12
pyenv local 3.12
pipenv --python $(pyenv which python)
pipenv install -d
```

### Prepare the DB
```
pipenv shell
python infoscience_exports/manage.py migrate --settings=settings.local
python infoscience_exports/manage.py createcachetable --settings=settings.local
```

## Run the project
```
pipenv shell
python infoscience_exports/manage.py runserver --settings=settings.local localhost:3000
```
Open http://localhost:3000/
