FROM python:3.12-slim

ARG DJANGO_ENV

ENV DJANGO_ENV=${DJANGO_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  PIPENV_HIDE_EMOJIS=true \
  NO_COLOR=true \
  PIPENV_NOSPIN=true \
  DEBIAN_FRONTEND=noninteractive

# install gettext
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        bash \
        gettext \
        postgresql-client \
        tree \
        curl \
        libevent-dev \
        rsync \
        nano \
        git \
    && rm -rf /var/cache/apt/ \
    && rm -rf /var/lib/apt/lists/*

# create directories
RUN mkdir -p /usr/src/app && \
    mkdir -p /usr/src/app/staticfiles && \
    mkdir -p /usr/src/app/infoscience_exports && \
    mkdir -p /var/log/django

WORKDIR /usr/src/app

# install requirements
COPY ./Pipfile /usr/src/app/Pipfile
COPY ./Pipfile.lock /usr/src/app/Pipfile.lock
RUN pip install pipenv
RUN /bin/bash -c 'pipenv install $(test "$DJANGO_ENV" == production || echo "--dev") --deploy --system --ignore-pipfile'

# copy project files
COPY ./update_release.py /usr/src/app/update_release.py
COPY ./infoscience_exports/exports/versions.py /usr/src/app/versions.py
COPY ./Makefile /usr/src/app/Makefile
COPY ./infoscience_exports /usr/src/app/infoscience_exports

# collectstatic
RUN DJANGO_SETTINGS_MODULE=settings.prod \
    SECRET_KEY="not needed to collectstaticfiles" \
    ALLOWED_HOSTS="not needed to collectstaticfiles" \
    SITE_URL="not needed to collectstaticfiles" \
    DATABASE_URL="not needed to collectstaticfiles" \
    python infoscience_exports/manage.py collectstatic

# compilemessages
RUN DJANGO_SETTINGS_MODULE=settings.prod \
    SECRET_KEY="not needed to compilemessages" \
    ALLOWED_HOSTS="not needed to compilemessages" \
    SITE_URL="not needed to compilemessages" \
    DATABASE_URL="not needed to compilemessages" \
    python infoscience_exports/manage.py compilemessages

VOLUME ["/usr/src/app/staticfiles", "/var/log/django", "/usr/src/app/coverage.xml"]

# set the root group advanced permissions, in case of live change
RUN chmod g+rwx -R /usr/src/app

EXPOSE 3000

CMD ["gunicorn", "--bind", ":3000", "--workers", "2", "--chdir", "/usr/src/app/infoscience_exports", "wsgi:application"]
