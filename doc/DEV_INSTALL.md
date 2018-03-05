# Getting up and running

First, choose if you want to run your application with Docker. If this is the case, go to INSTALL.rst. Otherwise, continue here.

## Prerequistes

The steps below will get you up and running with a local development environment. We assume you have the following installed:

* pip
* virtualenv / virtualwrapper
* PostgreSQL

## Requirements

In your virtualenv (activate), run::

    pip install -r ./requirements.txt

## Postgres install

Install PostgreSQL and some libraries::

    sudo apt-get install postgresql postgresql-client postgresql-server-dev-all libjpeg-dev

## Postgres config

Move to su::
    su

Be the postgres user::

    su - postgres

Create the user django, with django as password::

    createuser -SR -P django

    psql -c 'ALTER ROLE django WITH CREATEDB' -U postgres

create the db::

    createdb -O django infoscience_exports

    createdb -O django mock_infoscience_exports

## Django config

Do the first migration::

    fab migrate
    fab migrate_mock

It may be the good timing to set your environment variable::

    export DATABASE_PASSWORD='django'

Load mock data::

    python ./infoscience_exports/manage.py loaddata --app exports --database mock initial_data

Create your user::

    python ./infoscience_exports/manage.py createsuperuser

Verify with the tests::

    fab test

See by yourself live::

    fab serve

And go to `http://127.0.0.1:${DEV_PORT}/exports <http://127.0.0.1:8000/exports/>`_.

## How to start the development process

Here is the standard config to have a nice synchronisation with the different repositories. Let's suppose you have not any existing repository.

Don't forget to set tequila_user_name to the right value::

    git clone git@github.com:epfl-idevelop/infoscience-exports.git
    git remote add github git@github.com:epfl-idevelop/infoscience-exports.git
    git remote add gitlab git@gitlab.epfl.ch:infoscience/infoscience-exports.git
    git remote add epfl https://tequila_user_name@git.epfl.ch/repo/infoscience-exports.git
    git remote set-url --add origin git@gitlab.epfl.ch:infoscience/infoscience-exports.git
    git remote set-url --add origin https://tequila_user_name@git.epfl.ch/repo/infoscience-exports.git

This will work flawlessly with git push.

In the end, your .git/config should look like this::

    [core]
        repositoryformatversion = 0
        filemode = true
        bare = false
        logallrefupdates = true
    [remote "origin"]
        url = git@github.com:epfl-idevelop/infoscience-exports.git
        url = git@gitlab.epfl.ch:infoscience/infoscience-exports.git
        fetch = +refs/heads/*:refs/remotes/origin/*
    [remote "github"]
        url = git@github.com:epfl-idevelop/infoscience-exports.git
        fetch = +refs/heads/*:refs/remotes/github/*
    [remote "gitlab"]
        url = git@gitlab.epfl.ch:infoscience/infoscience-exports.git
        fetch = +refs/heads/*:refs/remotes/gitlab/*
    [remote "epfl"]
        url = https://tequila_user_name@git.epfl.ch/repo/infoscience-exports.git
        fetch = +refs/heads/*:refs/remotes/epfl/*
    [branch "master"]
        remote = origin
        merge = refs/heads/master
    [branch "develop"]
        remote = origin
        merge = refs/heads/develop
