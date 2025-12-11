# Infoscience-Exports
> Fetch and format Infoscience data

Configurable exports from Infoscience for your list of records

## Running locally

See [how to run locally](./DEV.md)

## Running with Docker

Here we expose the docker way to get started.
If you want to run locally with your own Django installed

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

You should be able to access http://localhost:3000 (add `/admin` if needed).


## Deploying
### Prerequisite
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
oc -n {your_namespace} rollout restart deployment/web-service
```

## Advanced configuration / Usages

Take a look into the [documentation folder](/doc)
