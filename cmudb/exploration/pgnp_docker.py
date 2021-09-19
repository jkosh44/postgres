import subprocess
import time
from typing import AnyStr, Tuple

from util import PRIMARY, REPLICA, execute_sys_command, ENV_FOLDER, CONTAINER_BIN_DIR, stop_process, OutputStrategy, \
    PROJECT_ROOT


# TODO use docker library (https://github.com/docker/docker-py)

def start_docker() -> subprocess.Popen:
    execute_sys_command("sudo docker volume create pgdata")
    execute_sys_command("sudo docker volume create pgdata2")
    execute_sys_command("sudo chown -R 1000:1000 /var/lib/docker/volumes/pgdata")
    execute_sys_command("sudo chown -R 1000:1000 /var/lib/docker/volumes/pgdata2")
    execute_sys_command(f"sudo docker build --tag pgnp --file {ENV_FOLDER}/Dockerfile {PROJECT_ROOT}")
    # Hide output because TPCC aborts clog stdout
    compose, _, _ = execute_sys_command(f"sudo docker-compose -f {ENV_FOLDER}/docker-compose-replication.yml up",
                                        block=False, output_strategy=OutputStrategy.Print)
    wait_for_pg_ready(PRIMARY)
    wait_for_pg_ready(REPLICA)
    return compose


def execute_in_container(container_name: str, cmd: str, block: bool = True,
                         output_strategy: OutputStrategy = OutputStrategy.Print) -> Tuple[
    subprocess.Popen, AnyStr, AnyStr]:
    docker_cmd = f'docker exec {container_name} /bin/bash -c'.split(" ")
    docker_cmd.append(f'{cmd}')

    return execute_sys_command(docker_cmd, block=block, output_strategy=output_strategy)


def is_pg_ready(container_name: str, port: int) -> bool:
    is_ready_res, _, _ = execute_in_container(container_name,
                                              f"{CONTAINER_BIN_DIR}/pg_isready --host {container_name} --port {port} "
                                              f"--username noisepage", output_strategy=OutputStrategy.Hide)
    return is_ready_res.returncode == 0


# TODO add timeout
def wait_for_pg_ready(container_name: str):
    while not is_pg_ready(container_name, 15721):
        time.sleep(1)


def shutdown_docker(docker_process: subprocess.Popen):
    stop_process(docker_process)
    execute_sys_command(f"sudo docker-compose -f {ENV_FOLDER}/docker-compose-replication.yml down --volumes")
    execute_sys_command("sudo docker volume rm pgdata")
    execute_sys_command("sudo docker volume rm pgdata2")
