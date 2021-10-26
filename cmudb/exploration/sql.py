import os
import subprocess
import time
from typing import List, Tuple

from pgnp_docker import execute_in_container
from util import execute_sys_command, OutputStrategy, CONTAINER_BIN_DIR, \
    stop_process, PGDATA_LOC


# SQL functionality

def execute_sql(query: str, port: int) -> List[str]:
    env = os.environ.copy()
    env["PGPASSWORD"] = "terrier"
    cmd = f"psql -h localhost -p {port} -U noisepage -t -P pager=off".split(" ")
    cmd.append(f'--command={query}')
    cmd.append("noisepage")
    sql_command, out, err = execute_sys_command(cmd, env=env,
                                                output_strategy=OutputStrategy.Capture)
    return [row.strip() for row in out.split("\n") if row.strip()]


def checkpoint(port: int) -> List[str]:
    return execute_sql("CHECKPOINT", port)


# Postgres functionality

def start_postgres_instance(container_name: str, port: int) -> subprocess.Popen:
    postgres_proc, _, _ = execute_in_container(container_name,
                                               f"{CONTAINER_BIN_DIR}/postgres -D {PGDATA_LOC} -p {port}",
                                               block=False)
    return postgres_proc


def stop_postgres_instance(postgres_process: subprocess.Popen):
    stop_process(postgres_process)


def is_pg_ready(container_name: str, port: int) -> bool:
    is_ready_res, _, _ = execute_in_container(container_name,
                                              f"{CONTAINER_BIN_DIR}/pg_isready --host {container_name} --port {port} "
                                              f"--username noisepage",
                                              output_strategy=OutputStrategy.Print)
    return is_ready_res.returncode == 0


# TODO add timeout
def wait_for_pg_ready(container_name: str, port: int, postgres_process: subprocess.Popen) -> bool:
    while not is_pg_ready(container_name,
                          port) and postgres_process.poll() is None:
        time.sleep(1)

    # Return code is only set when process exits and postgres proc shouldn't exit
    if postgres_process.returncode is not None:
        print(
            f"Postgres instance failed to start up with error code: {postgres_process.returncode}")
        return False

    return True


def start_and_wait_for_postgres_instance(container_name: str, port: int) -> Tuple[subprocess.Popen, bool]:
    proc = start_postgres_instance(container_name, port)
    valid = wait_for_pg_ready(container_name, port, proc)
    return proc, valid


def reset_wal(container_name: str):
    execute_in_container(container_name, f"{CONTAINER_BIN_DIR}/pg_resetwal -f {PGDATA_LOC}")
