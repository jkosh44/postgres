import subprocess
from typing import AnyStr, Tuple

import time

from util import PRIMARY, REPLICA, execute_sys_command, ENV_FOLDER, CONTAINER_BIN_DIR, stop_process, OutputStrategy, \
    PROJECT_ROOT, EXPLORATION


# TODO use docker library (https://github.com/docker/docker-py)

def start_docker() -> subprocess.Popen:
    execute_sys_command(f"sudo docker-compose -f {ENV_FOLDER}/docker-compose-replication.yml down --volumes")
    execute_sys_command("sudo docker volume rm pgdata-primary")
    execute_sys_command("sudo docker volume rm pgdata-replica")
    execute_sys_command("sudo docker volume create pgdata-primary")
    execute_sys_command("sudo docker volume create pgdata-replica")
    execute_sys_command("sudo chown -R 1000:1000 /mnt/docker/volumes/pgdata-primary")
    execute_sys_command("sudo chown -R 1000:1000 /mnt/docker/volumes/pgdata-replica")
    execute_sys_command("sudo docker network create --driver=bridge --subnet 172.19.253.0/30 tombstone")
    # Uncoment me
    # execute_sys_command(f"sudo docker build --tag pgnp --file {ENV_FOLDER}/Dockerfile {PROJECT_ROOT}")
    # Hide output because TPCC aborts clog stdout
    compose, _, _ = execute_sys_command(f"sudo docker-compose -f {ENV_FOLDER}/docker-compose-replication.yml up",
                                        block=False, output_strategy=OutputStrategy.Hide)
    wait_for_pg_ready(PRIMARY)
    wait_for_pg_ready(REPLICA)
    return compose


def start_exploration_docker() -> subprocess.Popen:
    execute_sys_command("sudo docker volume rm pgdata-exploration")
    execute_sys_command(f"sudo docker-compose -p exploratory -f {ENV_FOLDER}/docker-compose-exploration.yml down --volumes")
    execute_sys_command("sudo docker volume create pgdata-exploration")
    execute_sys_command("sudo chown -R 1000:1000 /mnt/docker/volumes/pgdata-exploration")
    compose, _, _ = execute_sys_command(f"sudo docker-compose -p exploratory -f {ENV_FOLDER}/docker-compose-exploration.yml up",
                                        block=False, output_strategy=OutputStrategy.Capture)

    # Hack to wait for container to start
    # time.sleep(5)
    # compose.stdout.flush()
    print("LOOK HERE FOR THE DEVIL")
    # print(f"Would terminate {'Exploring' in compose.stdout}")
    cont = True
    start = time.time()
    while cont:
        line = compose.stdout.readline()
        print(line)
        cont = "Exploring" not in line and time.time() - start < 10
        time.sleep(1)
    # for line in compose.stdout.readlines():
    #     print(line)
    # print(compose.stdout.)
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
    execute_sys_command("sudo docker volume rm pgdata-primary")
    execute_sys_command("sudo docker volume rm pgdata-replica")


def shutdown_exploratory_docker(exploratory_docker_process: subprocess.Popen):
    stop_process(exploratory_docker_process)
    execute_sys_command(f"sudo docker-compose -p exploratory -f {ENV_FOLDER}/docker-compose-exploration.yml down --volumes")
    execute_sys_command("sudo docker volume rm pgdata-exploration")
