# Infoscience-Exports
> Fetch and format Infoscience data

Configurable exports from Infoscience for your list of records

## Installing locally / Getting started

Here we expose the docker way to get started.

### Prerequisite

- Docker
- Docker-compose

### Initialize environnement variables

Start with:

```shell
make init-venv
```

Change the default values, if needed, by editing the .env file.
Then, check the result:

```shell
make vars
```

### Building / Running

Again, before building, assert your env vars are well set:

```shell
make vars
```

Build the images, run the containers and initialize the DB:

```shell
make up
```

You should be able to access https://127.0.0.1/ (add `/admin` if needed).


## Deploying
### Prerequiste
- Openshift
    - Have a running Openshift instance
- Keybase
    - Have access to the content of this folder
        - /keybase/team/epfl_idevfsd/infoscience-exports/
        
### Deploy        

- Asset Openshift is correctly configured:
```shell
./ansible/exportsible --dev
```

### Update the image with your machine
```shell
./ansible/exportsible -t local-build-and-push
```

#### Reload the pod with env changes (after per ex. a deployment edit, or a new image to deploy)
```shell
oc rollout restart deployment/web-service
```

## Advanced configuration / Usages

Take a look into the [documentation folder](/doc)
