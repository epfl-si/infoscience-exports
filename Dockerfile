FROM python:3

# install gettext
RUN apt-get update && apt-get install -y --no-install-recommends \
		gettext \
		tree \
	&& rm -rf /var/lib/apt/lists/*

# create directories
RUN mkdir -p /usr/src/app && \
	mkdir -p /usr/src/app/staticfiles && \
	mkdir -p /usr/src/app/infoscience_exports && \
	mkdir -p /var/log/django

WORKDIR /usr/src/app

# install requirements 
# (asap to make cache more efficent)
COPY ./requirements*.txt /usr/src/app/
RUN pip install -r requirements-dev.txt

# copy project files
COPY ./infoscience_exports /usr/src/app/infoscience_exports

# collectstatic
RUN DJANGO_SETTINGS_MODULE=settings.prod \ 
	SECRET_KEY="not needed to collectstaticfiles" \
	ALLOWED_HOST="not needed to collectstaticfiles" \
	SITE_URL="not needed to collectstaticfiles" \
	DATABASE_URL="not needed to collectstaticfiles" \
	python infoscience_exports/manage.py collectstatic

VOLUME ["/usr/src/app/staticfiles", "/var/log/django"]
