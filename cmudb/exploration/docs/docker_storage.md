## Docker Storage

### Overview
- All data is stored in writable container layer by default.
    - data doesn't persist after container is gone
    - Tightly coupled to the host machine
    - Requires storage driver
- Three options for persisting files:
    - Volumes
        - Stored in /var/lib/docker/volumes/
    - Bind Mounts
        - Can be stored anywhere in the host system
    - tmpfs mount (only on linux)
        - stored in host's memory only
- No matter what option is chosen it looks the same from within container

#### Volumes Overview
- Manager and created by Docker
- created with `docker volume create` or during container or service creation
- Stored within a directory on the Docker host
- When mounting the volume int a container, this directory is mounted into the container.
- A volume can be mounted into multiple containers simultaneously
- Remove unused volumes with `docker volume prune`
- Can give volumes names or keep them anonymous
- volume drivers allow you to store data on remote hosts or cloud providers or other possibilities

#### Bind Mounts
TODO - not using

#### tmpfs Mounts
TODO - not using


### Volumes
- Preferred mechanism for persisting data
- volume options when creating a service:
    - `-v` or -`--volume`: Three fields separated by `:` characters
        - first is name of the volume
        - second is path where the file/directory are mounted in the container
        - third is comma-separated list of options (optional)
    - `--mount`: Consists of multiple key-value pairs, separated by commas and each consisting of a `<key>=<value>` tuple.
        - `type`: `bind`, `volume`, or `tmpfs`
        - `source`: name of volume
        - `destination`: path where file/directory is mounted in the container
        - `readonly`: causes the bind mount to be read only
        - `volume-opt`: options
        - ex: ```docker service create \
          --mount 'type=volume,src=<VOLUME-NAME>,dst=<CONTAINER-PATH>,volume-driver=local,volume-opt=type=nfs,volume-opt=device=<nfs-server>:<nfs-path>,"volume-opt=o=addr=<nfs-address>,vers=4,soft,timeo=180,bg,tcp,rw"'
          --name myservice \
          <IMAGE>```
    - `--mount` is preferred to `--volume`
- Create volume: `docker volume create <volume-name>`
- List volume: `docker volume ls`
- Inspect a volume: `docker volume inspect <volume-name>`
- Remove a volume: `docker volume rm <volume-name>`
- Starting a container with a volume that doesn't exist creates the volume
  - ex: ```docker run -d \
    --name devtest \
    --mount source=myvol2,target=/app \
    nginx:latest```

#### Volumes with docker-compose
- General Syntax:
```yaml
services:
  <service-name>:
    volumes:
      <volume-name>:/path/in/container
volumes:
  <volume-name>:
```
- `volumes` sections:
  - `<volume-name>`: specifies the name of the volume 
    - `driver`: specifies which driver the volume should use
    - `driver_opts`: specify a list of options as key value pairs to pass to the driver (driver dependent)
    - `external`: if set to true it specifies that this volume has been created outside of Compose, so it's not created
    - `labels`: Adds metadata to containers
    - `name`: Sets a custom name for the volume


- To change location of docker directory change `--data-root` param in `/lib/systemd/system/docker.service` 