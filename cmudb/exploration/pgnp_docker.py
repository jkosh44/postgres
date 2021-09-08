import signal
import subprocess

import time

from util import PRIMARY, REPLICA, execute_sys_command, ENV_FOLDER, CONTAINER_BIN_DIR, PROJECT_ROOT


# TODO use docker library (https://github.com/docker/docker-py)

def start_docker() -> subprocess.Popen:
    # TODO uncomment me
    execute_sys_command(f"docker build --tag pgnp --file {ENV_FOLDER}/Dockerfile {PROJECT_ROOT}")
    compose = execute_sys_command(f"docker-compose -f {ENV_FOLDER}/docker-compose-replication.yml up", block=False)
    wait_for_pg_ready(PRIMARY)
    wait_for_pg_ready(REPLICA)
    return compose


# TODO this doesn't really work if cmd has any spaces....
def execute_in_container(container_name: str, cmd: str, block: bool = True, forward_output: bool = True):
    docker_cmd = f'docker exec {container_name} /bin/bash -c'.split(" ")
    docker_cmd.append(f'{cmd}')

    return execute_sys_command(docker_cmd, block, forward_output)


def is_pg_ready(container_name: str) -> bool:
    is_ready_res = execute_in_container(container_name,
                                        f"{CONTAINER_BIN_DIR}pg_isready --host {container_name} --port 15721 --username"
                                        f" noisepage",
                                        forward_output=False)
    return is_ready_res.returncode == 0


# TODO add timeout
def wait_for_pg_ready(container_name: str):
    while not is_pg_ready(container_name):
        time.sleep(1)


def shutdown_docker(docker_process: subprocess.Popen):
    docker_process.send_signal(signal.SIGINT)
    docker_process.communicate()
