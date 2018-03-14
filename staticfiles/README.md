# Static files

## Production

The static files needed for production are included in the Docker image. They are generated at build time, with the production settings:

    # Dockerfile
    RUN DJANGO_SETTINGS_MODULE=settings.prod \
        SECRET_KEY="not needed to collectstaticfiles" \
        ALLOWED_HOSTS="not needed to collectstaticfiles" \
        SITE_URL="not needed to collectstaticfiles" \
        DATABASE_URL="not needed to collectstaticfiles" \
        python infoscience_exports/manage.py collectstatic

## Developement

When developping, the static files are overriden in the container with a mounted volume

    # docker-compose-dev.yml
    web:
      ...
      volumes:
        - ./staticfiles:/usr/src/app/staticfiles

The developer can generate the static files within the container with:

    make static

or, if he wants to use his proper options:

    python infoscience_exports/manage.py collectstatic
