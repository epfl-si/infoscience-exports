Initial setup with Docker
=========================

Express set-up
--------------

0. Pre-requisite
................

- git repo checked out (`git clone git@github.com:epfl-idevelop/infoscience-exports.git`)

1. initialize a fresh .env file
...............................

.. code-block:: bash

    $ make init-venv
    ...

You might want to change the default values for the following vars:

- DJANGO_SETTINGS_MODULE=settings.dev
- SITE_URL=https://your-host.epfl.ch
- ALLOWED_HOST=your-host
- DEV_PORT=443

You can check what values will be taken into account with 

.. code-block:: bash

    $ make vars
    App-related vars:
      SECRET_KEY="SeLKDmig0mYF04WVkpZ6mowJ1FiodYkC0C4ZV6Rkuvc="
      DJANGO_SETTINGS_MODULE=settings.dev
      SITE_URL=https://127.0.0.1:8080
      ALLOWED_HOST=127.0.0.1
      DATABASE_URL=postgres://django:django@postgres:5432/infoscience_exports
      MOCKS_DATABASE_URL=postgres://django:django@postgres:5432/mock_infoscience_exports

    Dev-related vars:
      DEV_PORT=8080

2. Setup containers and DB 
..........................

.. code-block:: bash

    $ make init-docker
    $ make init-db

or the following alias 

.. code-block:: bash

    $ make reset


Development
-----------

You can access, with the default configuration :

* the app itself

  * any gaspar credential
  * https://127.0.0.1:8000/

* its admin

  * with the service account *infoscience-exports*
  * or with a gaspar account which has received admin rights
  * https://127.0.0.1:8000/admin


To deploy a new version of your code (without losing data) ::

    $ make deploy

To rebuild everything from scratch ::

    $ make reset

This command can actually be split in two parts if you only want to reset docker / db ::

    $ make init-docker
    ...
    $ make init-db

To run the tests ::

    $ docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py test exports --noinput [--failfast --keepdb]

Or to test more intensively with nose and coverage ::

    $ docker-compose -f docker-compose-dev.yml exec web infoscience_exports/manage.py test exports --noinput [-x]

To check your environment variables ::

    # on your host
    $ make vars

    # inside the web container
    $ docker-compose -f docker-compose-dev.yml run web env


A few words on config
---------------------

Three docker images will be pulled / build on the following command. Those docker images are the same for all environments. 

Production
..........

Files are copied inside the images for production purpose. 

* the code of the application: ./infoscience_exports
* the generated static files:  ./staticfiles

Once the images built, just run the containers with ::

    $ docker-compose up

If you want to run the containers as a daemon, use the -d option. Logs are still available on demand ::

    $ docker-compose up -d
    $ docker-compose logs


Development
...........

For development purpose, those files can also be mounted with local tree structure ::

    $ docker-compose -f docker-compose-dev.yml up

You will thus be allowed to get change on the fly :

* the code of the application: ./infoscience_exports
* the generated static files:  ./staticfiles
* some assets you might need:  ./nginx/assets
* the nginx configuration:     ./nginx/sites-enabled/web.conf

Aside from the volumes, docker-compose-dev.yml  also makes use of 

* .env to load environment variables
* settings/dev.py to set django settings

Would you need to connect directly to the DB, we exposed an access to the host on port 25432 ::

    $ psql -h 127.0.0.1 -p 25432 -U django -W infoscience_exports

