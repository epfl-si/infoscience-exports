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

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        bash \
        gettext \
        postgresql-client \
        tree \
        curl \
        libevent-dev \
        rsync \
        cron \
        nano \
        git \
        procps \
    && rm -rf /var/cache/apt/ \
    && rm -rf /var/lib/apt/lists/*

# create directories
RUN mkdir -p /usr/src/app && \
    mkdir -p /usr/src/app/staticfiles && \
    mkdir -p /usr/src/app/infoscience_exports && \
    mkdir -p /var/log/django/infoscience-exports

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

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

VOLUME ["/usr/src/app/staticfiles", "/var/log/django"]

# Set ownership and permissions for running locally (UID 1000) or in OpenShift (which uses the root group (GID 0) for containers)
# https://developers.redhat.com/blog/2020/10/26/adapting-docker-and-kubernetes-containers-to-run-on-red-hat-openshift-container-platform#group_ownership_and_file_permission
RUN chown -R 1000:0 /usr/src/app/staticfiles /var/log/django && \
  chmod -R ug+rwx /usr/src/app/staticfiles /var/log/django

USER 1000

EXPOSE 3000

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
