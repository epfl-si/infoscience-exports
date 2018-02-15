Initial setup with Docker
=========================

What you do not get with the pull
---------------------------------

You will miss two directories :

* env
* staticfiles

In the first one, you will need to create two files :

* django.env ::

   SECRET_KEY=your-secret
   DATABASE_PASSWORD_PROD=django

* django-dev.env ::

   SECRET_KEY=your-secret
   DATABASE_PASSWORD_DEV=django

A few words on config
---------------------

Three docker images (postgres, web, nginx) will be pulled / build on the following command. Those docker images are the same for all environments. 

Production
..........

The production make use of one more container, from a standard redis image ::

    $ docker-compose build
    postgres uses an image, skipping
    redis uses an image, skipping
    Building web
    ... (7 steps)
    Building nginx
    ... (4 steps)

Files are copied inside the images for production purpose. 

* the code of the application: ./infoscience_exports
* the generated static files:  ./staticfiles
* some assets you might need:  ./nginx/assets
* the nginx configuration:     ./nginx/sites-enabled/web.conf

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

* env/django-dev.env to define passwords (set in environment variables)
* settings/dev.py to set django settings

Would you need to connect directly to the DB, we exposed an access to the host on port 25432 ::

    $ psql -h localhost -p 25432 -U django -W infoscience_exports

Express set-up
--------------

For dev ::
    
    $ docker-compose build
    $ docker-compose -f docker-compose-dev.yml up -d


Initialize the docker app this way. Please, replace the names with your previous choices::

    $ docker exec -it infoscienceexports_postgres_1 /bin/bash
    root@xxx:/# createuser -dSR django -P -U postgres
      Enter password for new role: django
      Enter it again: django
    root@xxx:/# createdb -O django infoscience_exports -U postgres
    root@xxx:/# createdb -O django mock_infoscience_exports -U postgres

To set up data and static files ::

    $ docker-compose -f docker-compose-dev.yml run web python infoscience_exports/manage.py migrate
    $ docker-compose -f docker-compose-dev.yml run web python infoscience_exports/manage.py migrate --database=mock
    $ docker-compose -f docker-compose-dev.yml run web python infoscience_exports/manage.py collectstatic --noinput

To create your super user ::

    $ docker-compose -f docker-compose-dev.yml run web python infoscience_exports/manage.py createsuperuser

To run the tests ::

    $ docker-compose -f docker-compose-dev.yml exec web python infoscience_exports/manage.py test exports --noinput [--failfast --keepdb]

Or to test more intensively with nose and coverage ::

    $ docker-compose -f docker-compose-dev.yml exec web infoscience_exports/manage.py test exports --noinput [-x]

To check your environment variables ::

    $ docker-compose -f docker-compose-dev.yml run web env

You can then access the app with

* its CRUD interface : http://127.0.0.1:8000/exports/
* or the API : http://127.0.0.1:8000/api/v1/exports/
* or through admin: http://127.0.0.1:8000/admin/login

And, finally, go on with your nice feature ::

    $ git checkout -b my-nice-feature master
    ...
    $ git push -u origin my-nice-feature
    ...
    $ git push

check this link for nice description of the git workflow: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow 
