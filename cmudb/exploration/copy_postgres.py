import subprocess
from functools import reduce
from typing import Tuple

import time

from benchbase import cleanup_benchbase, run_benchbase, setup_benchbase
from pgnp_docker import start_docker, shutdown_docker, execute_in_container, is_pg_ready, start_exploration_docker, \
    shutdown_exploratory_docker
from sql import execute_sql, validate_sql_results, validate_table_has_values
from util import REPLICA, CONTAINER_BIN_DIR, PGDATA_LOC, PGDATA2_LOC, EXPLORATION_PORT, \
    stop_process, OutputStrategy, PRIMARY_PORT, PGDATA_REPLICA_LOC, EXPLORATION

RESULT_FILE = "./experiment_{}.json"


# TODO extract constants
def load_validation_data():
    execute_sql("CREATE TABLE foo(a int);", PRIMARY_PORT)
    execute_sql("INSERT INTO foo VALUES (42), (666);", PRIMARY_PORT)


def copy_pgdata() -> int:
    start = time.time_ns()
    execute_in_container(EXPLORATION, f"sudo cp -a {PGDATA_REPLICA_LOC}/* {PGDATA_LOC}")
    end = time.time_ns()
    execute_in_container(EXPLORATION, f"sudo chown terrier:terrier -R {PGDATA_LOC}")
    execute_in_container(EXPLORATION, f"rm {PGDATA_LOC}/postmaster.pid")
    execute_in_container(EXPLORATION, f"rm {PGDATA_LOC}/standby.signal")
    return end - start


def start_exploration_postgres() -> Tuple[subprocess.Popen, int, bool]:
    start = time.time_ns()
    exploration_proc, _, _ = execute_in_container(EXPLORATION,
                                                  f"{CONTAINER_BIN_DIR}/postgres -D {PGDATA_LOC} -p {EXPLORATION_PORT}",
                                                  block=False)

    while not is_pg_ready(EXPLORATION, EXPLORATION_PORT) and exploration_proc.poll() is None:
        time.sleep(1)

    # Return code is only set when process exits and exploration proc is daemon (shouldn't exit)
    end = time.time_ns()
    total_time = end - start
    if exploration_proc.returncode is not None:
        print(f"Exploration instance failed to start up with error code: {exploration_proc.returncode}")
        return exploration_proc, total_time, False

    return exploration_proc, total_time, True


def stop_exploration_postgres(exploration_process: subprocess.Popen):
    stop_process(exploration_process)


def validate_exploration_process() -> bool:
    tables = ["usertable"]
    return \
        validate_sql_results(execute_sql("SELECT * FROM foo", EXPLORATION_PORT), ['42', '666']) \
        and reduce(lambda a, b: a and b, [validate_table_has_values(table, EXPLORATION_PORT) for table in tables])


def test_copy() -> Tuple[int, int, bool]:
    print("Starting exploration container")
    exploratory_container = start_exploration_docker()
    print("Exploration container started")
    print("Copying replica data")
    copy_time_ns = copy_pgdata()
    print("Exploration data copied")
    print("Starting exploration postgres instance")
    exploration_process, startup_time, valid = start_exploration_postgres()
    if not valid:
        stop_exploration_postgres(exploration_process)
        shutdown_exploratory_docker(exploratory_container)
        return copy_time_ns, startup_time, valid
    print("Exploration postgres instance started")
    valid = validate_exploration_process()
    print("Killing exploration postgres process")
    stop_exploration_postgres(exploration_process)
    print("Exploration postgres killed successfully")
    execute_in_container(EXPLORATION, f"sudo rm -rf {PGDATA2_LOC}/*")
    print("Killing exploration container")
    shutdown_exploratory_docker(exploratory_container)
    print("Exploration container killed")
    return copy_time_ns, startup_time, valid


def collect_results(result_file: str, benchbase_proc: subprocess.Popen):
    # Incrementally write to file so we don't lose data in case of runtime failure
    with open(result_file, "w") as f:
        i = 0
        # TODO find out cleaner way to write json
        f.write("[\n")
        first_obj = True
        while benchbase_proc.poll() is None:
            copy_time_ns, startup_time, valid = test_copy()
            if not first_obj:
                f.write(",\n")
            f.write("\t{\n")
            f.write(f'\t\t"iteration": {i},\n')
            f.write(f'\t\t"copy_time_ns": {copy_time_ns},\n')
            f.write(f'\t\t"startup_time_ns": {startup_time},\n')
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

    execute_sql("ALTER SYSTEM SET log_min_error_statement TO 'FATAL';", 15721)
    execute_sql("ALTER SYSTEM SET log_min_error_statement TO 'FATAL';", 15722)

    # Load some data into primary for validation
    load_validation_data()

    setup_benchbase()
    print("Loading data")
    run_benchbase(create=True, load=True, execute=False)
    print("Data loaded")

    result_file = RESULT_FILE.format(time.time())

    benchbase_proc = run_benchbase(create=False, load=False, execute=True, block=False,
                                   output_strategy=OutputStrategy.Hide)

    collect_results(result_file, benchbase_proc)

    cleanup_benchbase()
    print("Killing Docker containers")
    shutdown_docker(docker_process)
    print("Docker containers killed successfully")


if __name__ == "__main__":
    main()
