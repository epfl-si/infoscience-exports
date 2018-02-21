Initial setup with Docker
=========================

Express set-up
--------------

Pre-requisite

- git repo checked out (`git clone git@github.com:epfl-idevelop/infoscience-exports.git`)


For dev ::
    
    $ make init-venv
    ...
    -> update env vars

You might want to change the default values for the following vars:

- DJANGO_SETTINGS_MODULE=settings.dev
- SITE_URL=https://your-host.epfl.ch
- ALLOWED_HOST=your-host
- DEV_PORT=80

.. code-block:: bash

    $ make init-docker
    $ make init-db

To set up data and static files ::

    $ docker-compose -f docker-compose-dev.yml run web python infoscience_exports/manage.py migrate --database=mock
    $ docker-compose -f docker-compose-dev.yml run web python infoscience_exports/manage.py collectstatic --noinput

To create your super user, customize and run this line ::

    $ docker-compose -f docker-compose-dev.yml run web python infoscience_exports/manage.py createsuperuser --username=your_username --email=same_as_tequila

To run the tests ::

    $ docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py test exports --noinput [--failfast --keepdb]

Or to test more intensively with nose and coverage ::

    $ docker-compose -f docker-compose-dev.yml exec web infoscience_exports/manage.py test exports --noinput [-x]

To check your environment variables ::

    $ docker-compose -f docker-compose-dev.yml run web env

You can then access the app with

* its CRUD interface : https://127.0.0.1:${DEV_PORT}/exports/
* or the API : https://127.0.0.1:${DEV_PORT}/api/v1/exports/
* or through admin: https://127.0.0.1:${DEV_PORT}/admin

And, finally, go on with your nice feature ::

    $ git checkout -b my-nice-feature master
    ...
    $ git push -u origin my-nice-feature
    ...
    $ git push

check this link for nice description of the git workflow: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow 


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

