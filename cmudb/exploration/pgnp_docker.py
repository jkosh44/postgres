import subprocess
import time
from typing import AnyStr, Tuple

from util import execute_sys_command, ENV_FOLDER, stop_process, OutputStrategy, \
    UTF_8, PROJECT_ROOT, EXPLORATORY_COMPOSE, \
    EXPLORATION_VOLUME_POOL, \
    EXPLORATORY_PROJECT_NAME, IMAGE_TAG


# TODO use docker library (https://github.com/docker/docker-py)

# Docker Utilities

def build_image(tag: str):
    execute_sys_command(f"sudo docker build --tag {tag} --file {ENV_FOLDER}/Dockerfile {PROJECT_ROOT}")


def remove_volume(volume_name: str):
    execute_sys_command(f"sudo docker volume rm {volume_name}")


def create_volume(docker_volume_dir: str, volume_name: str):
    execute_sys_command(f"sudo docker volume create {volume_name}")
    execute_sys_command(f"sudo chown -R 1000:1000 {docker_volume_dir}/{volume_name}")


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
                         output_strategy: OutputStrategy = OutputStrategy.Print) -> \
        Tuple[subprocess.Popen, AnyStr, AnyStr]:
    docker_cmd = f'docker exec {container_name} /bin/bash -c'.split(" ")
    docker_cmd.append(f'{cmd}')

    return execute_sys_command(docker_cmd, block=block, output_strategy=output_strategy)


# Exploratory functionality

def setup_docker_env(docker_volume_dir: str):
    cleanup_docker_env(docker_volume_dir)
    build_image(IMAGE_TAG)


def cleanup_docker_env(docker_volume_dir: str):
    destroy_container(EXPLORATORY_COMPOSE, EXPLORATORY_PROJECT_NAME)
    remove_exploratory_data(docker_volume_dir)
    remove_volume(EXPLORATION_VOLUME_POOL)


def start_exploration_docker(docker_volume_dir: str) -> subprocess.Popen:
    create_volume(docker_volume_dir, EXPLORATION_VOLUME_POOL)
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


def shutdown_exploratory_docker(exploratory_docker_process: subprocess.Popen, docker_volume_dir: str):
    stop_container(exploratory_docker_process)
    cleanup_docker_env(docker_volume_dir)


def remove_exploratory_data(docker_volume_dir: str):
    execute_sys_command(f"sudo rm -rf {docker_volume_dir}/{EXPLORATION_VOLUME_POOL}")
