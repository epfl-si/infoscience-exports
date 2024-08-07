# Infoscience-Exports
> Fetch and format Infoscience data

Configurable exports from Infoscience for your list of records

## Installing locally / Getting started

Here we expose the docker way to get started. To get along without docker, 
see [this documentation](/doc/DEV_INSTALL.md). 

### Prerequisite

- Make
- pipenv
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

Again, before building, assert your env vars are well setted:

```shell
make vars
```

Build the images, run the containers and initialize the DB:

```shell
make init
```

Get the working url:
```shell
make show-app-url
```
Depending on your envs, it may be https://127.0.0.1:3000/publication-exports/.

And check the result with your favorite browser on it (add `/admin` if needed).

Later you can start the stack with:

```shell
make up
```

and stop with:
```shell
make stop
```

## Developing

### Prerequisite

The first thing to do is enable a post-commit git hook in order to have the versions taken care of

```shell
cp update_release.py .git/hooks/post-commit
```

This hook will update automagically the file './versions.py' on each commit, so you are ready to release new versions.

### Develop 
### Release
When you are happy with your changes, you can release a new version.

First, be sure to have the [Changelog Generator](https://github.com/github-changelog-generator/github-changelog-generator) installed: 
```shell
sudo gem install github_changelog_generator
```

Then, create the release:

```shell
make release
```

This will take care of creating the version number, the branches, the tags, the changelog and the github release.

## Deploying
### Prerequiste
- Openshift
    - Have a running Openshift instance
- Keybase
    - Have access to the content of this folder
        - /keybase/team/epfl_idevfsd.devrun/infoscience-exports/
        
### Deploy        

- Asset Openshift is correctly configured:
```shell
./ansible/exportsible
```

- Start the local compilation, and send the new image to openshift:
```shell
./ansible/exportsible -t update-image-with-local
```

#### Reload the pod with env changes (after per ex. a deployment edit, or a new image to deploy)
```shell
oc rollout restart deployment/infoscience-exports
```

## Advanced configuration / Usages

Take a look into the [documentation folder](/doc)
