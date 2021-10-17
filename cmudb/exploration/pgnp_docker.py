import subprocess
import time
from typing import AnyStr, Tuple

from util import execute_sys_command, ENV_FOLDER, stop_process, OutputStrategy, \
    UTF_8, PROJECT_ROOT

PRIMARY_VOLUME = "pgdata-primary"
REPLICA_VOLUME = "pgdata-replica"
EXPLORATION_VOLUME = "pgdata-exploration"

DOCKER_VOLUME_DIR = "/mnt/docker/volumes"

REPLICATION_COMPOSE = "docker-compose-replication.yml"
EXPLORATORY_COMPOSE = "docker-compose-exploration.yml"

REPLICATION_PROJECT_NAME = "replication"
EXPLORATORY_PROJECT_NAME = "exploratory"

IMAGE_TAG = "pgnp"


# TODO use docker library (https://github.com/docker/docker-py)

# Docker Utilities

def build_image(tag: str):
    execute_sys_command(f"sudo docker build --tag {tag} --file {ENV_FOLDER}/Dockerfile {PROJECT_ROOT}")


def remove_volume(volume_name: str):
    execute_sys_command(f"sudo docker volume rm {volume_name}")


def create_volume(volume_name: str):
    execute_sys_command(f"sudo docker volume create {volume_name}")
    execute_sys_command(f"sudo chown -R 1000:1000 {DOCKER_VOLUME_DIR}/{volume_name}")


def create_container(compose_yml: str, project_name: str, output_strategy: OutputStrategy) -> subprocess.Popen:
    compose, _, _ = execute_sys_command(
        f"sudo docker-compose -p {project_name} -f {ENV_FOLDER}/{compose_yml} up",
        block=False, output_strategy=output_strategy)
    return compose


def stop_container(container: subprocess.Popen):
    stop_process(container)


def destroy_container(compose_yml: str, project_name: str):
    execute_sys_command(f"sudo docker-compose -p {project_name} -f {ENV_FOLDER}/{compose_yml} down --volumes")


def execute_in_container(container_name: str, cmd: str, block: bool = True,
                         output_strategy: OutputStrategy = OutputStrategy.Print) -> Tuple[
    subprocess.Popen, AnyStr, AnyStr]:
    docker_cmd = f'docker exec {container_name} /bin/bash -c'.split(" ")
    docker_cmd.append(f'{cmd}')

    return execute_sys_command(docker_cmd, block=block, output_strategy=output_strategy)


# Exploratory functionality

def setup_docker_env():
    cleanup_docker_env()
    build_image(IMAGE_TAG)


def cleanup_docker_env():
    destroy_container(REPLICATION_COMPOSE, REPLICATION_PROJECT_NAME)
    destroy_container(EXPLORATORY_COMPOSE, EXPLORATORY_PROJECT_NAME)
    remove_volume(PRIMARY_VOLUME)
    remove_volume(REPLICA_VOLUME)
    remove_volume(EXPLORATION_VOLUME)


def start_replication_docker() -> subprocess.Popen:
    create_volume(PRIMARY_VOLUME)
    create_volume(REPLICA_VOLUME)
    # Make sure that container doesn't reuse machine's IP address
    execute_sys_command("sudo docker network create --driver=bridge --subnet 172.19.253.0/30 tombstone")
    # Hide output because TPCC aborts clog stdout
    return create_container(REPLICATION_COMPOSE, REPLICATION_PROJECT_NAME, OutputStrategy.Print)


def start_exploration_docker() -> subprocess.Popen:
    create_volume(EXPLORATION_VOLUME)
    compose = create_container(EXPLORATORY_COMPOSE, EXPLORATORY_PROJECT_NAME, OutputStrategy.Capture)

    # TODO Hack to wait for container to start
    docker_not_started = True
    while docker_not_started:
        line = compose.stdout.readline()
        if line is not None:
            line = line.decode(UTF_8)
        print(line)
        docker_not_started = "Exploring" not in line and compose.poll() is None
        time.sleep(10)
    return compose


def shutdown_replication_docker(docker_process: subprocess.Popen):
    stop_container(docker_process)
    destroy_container(REPLICATION_COMPOSE, REPLICATION_PROJECT_NAME)
    remove_volume(PRIMARY_VOLUME)
    remove_volume(REPLICA_VOLUME)


def shutdown_exploratory_docker(exploratory_docker_process: subprocess.Popen):
    stop_container(exploratory_docker_process)
    destroy_container(EXPLORATORY_COMPOSE, EXPLORATORY_PROJECT_NAME)
    remove_volume(EXPLORATION_VOLUME)
