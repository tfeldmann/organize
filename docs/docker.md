# Using the organize docker image

The organize docker image comes preinstalled with `exiftool` and `pdftotext` as well as
all the python dependencies set up and ready to go.

!!! note

    As organize is mainly used for moving files around you have to be careful about your
    volume mounts and paths. If you move a file to a folder which is not persisted
    it is gone as soon as the container is stopped!

## Building the image

`cd` into the organize folder (containing `Dockerfile`) and build the image:

```sh
docker build -t organize .
```

The image is now tagged as `organize`. Now you can test the image by running

```sh
docker run --rm organize
```

This will show the organize usage help text.

## Running

Let's create a basic config file `docker-conf.yml`:

```yml
rules:
  - locations: /data
    actions:
      - echo: "Found file: {path}"
```

We can now run mount the config file to the container path `/config/config.yml`. The current directory is mounted to `/data` so we have some files present.
We can now start the container:

```sh
docker run --rm -v ./docker-conf.yml:/config/config.yml -v .:/data organize run
```

### Passing the config file from stdin

Instead of mounting the config file into the container you can also pass it from stdin:

```sh
docker run -i --rm organize check --stdin < ./docker-conf.yml
```
