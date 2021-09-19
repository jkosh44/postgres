import os
import subprocess
import time
from functools import reduce
from typing import List, Tuple

from benchbase import cleanup_benchbase, run_benchbase, setup_benchbase
from pgnp_docker import start_docker, shutdown_docker, execute_in_container, is_pg_ready
from util import execute_sys_command, REPLICA, CONTAINER_BIN_DIR, PGDATA_LOC, PGDATA2_LOC, EXPLORATION_PORT, \
    stop_process, OutputStrategy, PRIMARY_PORT

RESULT_FILE = "./experiment_{}.json"


def execute_sql(query: str, port: int) -> List[str]:
    env = os.environ.copy()
    env["PGPASSWORD"] = "terrier"
    cmd = f"psql -h localhost -p {port} -U noisepage -t -P pager=off".split(" ")
    cmd.append(f'--command={query}')
    cmd.append("noisepage")
    sql_command, out, err = execute_sys_command(cmd, env=env, output_strategy=OutputStrategy.Capture)
    return [row.strip() for row in out.split("\n") if row.strip()]


# TODO extract constants
def load_validation_data():
    execute_sql("CREATE TABLE foo(a int);", PRIMARY_PORT)
    execute_sql("INSERT INTO foo VALUES (42), (666);", PRIMARY_PORT)


# SQL results are unordered bag so we need to check that each list has the same amount of each item
def validate_sql_results(results: List[str], expected: List[str]) -> bool:
    expected_map = {}
    for row in expected:
        if row not in expected_map:
            expected_map[row] = 0
        expected_map[row] += 1

    for row in results:
        if row not in expected_map:
            print(f"SQL query results {results} do not match expected {expected}")
            return False
        expected_map[row] -= 1

    for val in expected_map.values():
        if val != 0:
            print(f"SQL query results {results} do not match expected {expected}")
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


def copy_pgdata() -> int:
    start = time.time_ns()
    execute_in_container(REPLICA, f"sudo cp -a {PGDATA_LOC}/* {PGDATA2_LOC}")
    end = time.time_ns()
    execute_in_container(REPLICA, f"sudo chown terrier:terrier -R {PGDATA2_LOC}")
    execute_in_container(REPLICA, f"rm {PGDATA2_LOC}/postmaster.pid")
    execute_in_container(REPLICA, f"rm {PGDATA2_LOC}/standby.signal")
    return end - start


def start_exploration_postgres() -> Tuple[subprocess.Popen, bool]:
    exploration_proc, _, _ = execute_in_container(REPLICA,
                                                  f"{CONTAINER_BIN_DIR}/postgres -D {PGDATA2_LOC} -p {EXPLORATION_PORT}",
                                                  block=False)

    while not is_pg_ready(REPLICA, EXPLORATION_PORT) and exploration_proc.poll() is None:
        time.sleep(1)

    # Return code is only set when process exits and exploration proc is daemon (shouldn't exit)
    return exploration_proc, exploration_proc.returncode is not None


def stop_exploration_postgres(exploration_process: subprocess.Popen):
    stop_process(exploration_process)


def validate_exploration_process() -> bool:
    tables = ["usertable"]
    return \
        validate_sql_results(execute_sql("SELECT * FROM foo", EXPLORATION_PORT), ['42', '666']) \
        and reduce(lambda a, b: a and b, [validate_table_has_values(table, EXPLORATION_PORT) for table in tables])


def test_copy():
    print("Starting exploration postgres instance")
    copy_time_ns = copy_pgdata()
    exploration_process, valid = start_exploration_postgres()
    if not valid:
        return copy_time_ns, valid
    print("Exploration postgres instance started")
    valid = validate_exploration_process()
    print("Killing exploration postgres process")
    stop_exploration_postgres(exploration_process)
    print("Exploration postgres killed successfully")
    execute_in_container(REPLICA, f"sudo rm -rf {PGDATA2_LOC}/*")
    return copy_time_ns, valid


def collect_results(result_file: str, benchbase_proc: subprocess.Popen):
    # Incrementally write to file so we don't lose data in case of runtime failure
    with open(result_file, "w") as f:
        i = 0
        # TODO find out cleaner way to write json
        f.write("[\n")
        first_obj = True
        while benchbase_proc.poll() is None:
            copy_time_ns, valid = test_copy()
            if not first_obj:
                f.write(",\n")
            f.write("\t{\n")
            f.write(f'\t\t"iteration": {i},\n')
            f.write(f'\t\t"copy_time_ns": {copy_time_ns},\n')
            f.write(f'\t\t"valid": {"true" if valid else "false"}\n')
            f.write("\t}")
            i += 1
            first_obj = False
        f.write("\n")
        f.write("]\n")


def main():
    print("Starting Docker containers")
    docker_process = start_docker()
    print("Docker containers started successfully")

    # Load some data into primary for validation
    load_validation_data()

    setup_benchbase()
    print("Loading data")
    run_benchbase(create=True, load=True, execute=False)
    print("Data loaded")

    result_file = RESULT_FILE.format(time.time())

    benchbase_proc = run_benchbase(create=False, load=False, execute=True, block=False)

    collect_results(result_file, benchbase_proc)

    cleanup_benchbase()
    print("Killing Docker containers")
    shutdown_docker(docker_process)
    print("Docker containers killed successfully")


if __name__ == "__main__":
    main()
