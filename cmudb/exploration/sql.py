import os
import subprocess
from typing import List, Tuple

import time

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


# SQL results are unordered bag so we need to check that each list has the same amount of each item
def validate_sql_results(results: List[str], expected: List[str]) -> bool:
    expected_map = {}
    for row in expected:
        if row not in expected_map:
            expected_map[row] = 0
        expected_map[row] += 1

    for row in results:
        if row not in expected_map:
            print(
                f"SQL query results {results} do not match expected {expected}")
            return False
        expected_map[row] -= 1

    for val in expected_map.values():
        if val != 0:
            print(
                f"SQL query results {results} do not match expected {expected}")
            return False

    return True


def count_table_sql(table: str, port: int) -> int:
    res = execute_sql(f"SELECT COUNT(*) FROM {table}", port)
    if len(res) != 1:
        print(f"Invalid res from table count. Table: {table}, Res: {res}")
        return -1
    res = res[0]
    if not res.isnumeric():
        print(f"Invalid res from table count. Table: {table}, Res: {res}")
        return -1
    return int(res)


def validate_table_has_values(table: str, port: int) -> bool:
    res = count_table_sql(table, port) > 0
    if not res:
        print(f"Table {table} has no data")
    return res


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
                                              output_strategy=OutputStrategy.Hide)
    return is_ready_res.returncode == 0


# TODO add timeout
def wait_for_pg_ready(container_name: str, port: int,
                      postgres_process: subprocess.Popen) -> bool:
    while not is_pg_ready(container_name,
                          port) and postgres_process.poll() is None:
        time.sleep(1)

    # Return code is only set when process exits and postgres proc shouldn't exit
    if postgres_process.returncode is not None:
        print(
            f"Postgres instance failed to start up with error code: {postgres_process.returncode}")
        return False

    return True


def start_and_wait_for_postgres_instance(container_name: str, port: int) -> \
Tuple[subprocess.Popen, bool]:
    proc = start_postgres_instance(container_name, port)
    valid = wait_for_pg_ready(container_name, port, proc)
    return proc, valid


def reset_wal(container_name: str, port: int):
    execute_in_container(container_name,
                         f"{CONTAINER_BIN_DIR}/pg_resetwal -f {PGDATA_LOC} -p {port}")
