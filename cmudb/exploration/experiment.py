import subprocess
from functools import reduce
from typing import Tuple

import time

from benchbase import cleanup_benchbase, run_benchbase, setup_benchbase
from data_copy import copy_pgdata_cow, destroy_exploratory_data_cow
from pgnp_docker import start_replication_docker, shutdown_replication_docker, \
    execute_in_container, \
    start_exploration_docker, \
    shutdown_exploratory_docker, setup_docker_env
from sql import execute_sql, validate_sql_results, validate_table_has_values, \
    checkpoint, \
    start_and_wait_for_postgres_instance, stop_postgres_instance, \
    wait_for_pg_ready, reset_wal
from util import PGDATA_LOC, PGDATA2_LOC, \
    EXPLORATION_PORT, \
    OutputStrategy, PRIMARY_PORT, EXPLORATION, \
    timed_execution, REPLICA, PRIMARY, REPLICA_PORT

RESULT_FILE = "./test_result_{}.json"


# TODO extract constants
def load_validation_data():
    execute_sql("CREATE TABLE foo(a int);", PRIMARY_PORT)
    execute_sql("INSERT INTO foo VALUES (42), (666);", PRIMARY_PORT)


def validate_exploration_process() -> bool:
    tables = ["usertable"]
    return \
        validate_sql_results(execute_sql("SELECT * FROM foo", EXPLORATION_PORT),
                             ['42', '666']) \
        and reduce(lambda a, b: a and b,
                   [validate_table_has_values(table, EXPLORATION_PORT) for table
                    in tables])


def test_copy() -> Tuple[int, int, int, int, int, int, bool]:
    # Start exploration instance
    print("Taking checkpoint")
    _, checkpoint_time_ns = timed_execution(checkpoint, REPLICA_PORT)
    print("Checkpoint complete")
    print("Copying replica data")
    _, copy_time_ns = timed_execution(copy_pgdata_cow)
    print("Exploration data copied")
    print("Starting exploration container")
    exploratory_container, docker_start_time_ns = timed_execution(
        start_exploration_docker)
    if exploratory_container.returncode is not None:
        shutdown_exploratory_docker(exploratory_container)
        destroy_exploratory_data_cow()
        return checkpoint_time_ns, copy_time_ns, docker_start_time_ns, 0, 0, 0, False
    execute_in_container(EXPLORATION,
                         f"sudo chown terrier:terrier -R {PGDATA_LOC}")
    execute_in_container(EXPLORATION, f"sudo chmod 700 -R {PGDATA_LOC}")
    execute_in_container(EXPLORATION, f"rm {PGDATA_LOC}/postmaster.pid")
    execute_in_container(EXPLORATION, f"rm {PGDATA_LOC}/standby.signal")
    print("Exploration container started")
    print("Starting exploration postgres instance")
    _, reset_wal_time = timed_execution(reset_wal, EXPLORATION,
                                        EXPLORATION_PORT)
    (exploration_process, valid), postgres_startup_time = timed_execution(
        start_and_wait_for_postgres_instance, EXPLORATION,
        EXPLORATION_PORT)
    if not valid:
        shutdown_exploratory_docker(exploratory_container)
        destroy_exploratory_data_cow()
        return checkpoint_time_ns, copy_time_ns, docker_start_time_ns, reset_wal_time, postgres_startup_time, 0, valid
    print("Exploration postgres instance started")

    # Validate exploration instance
    valid = validate_exploration_process()

    # Shutdown exploration instance
    print("Killing exploration postgres process")
    _, postgres_stop_time_ns = timed_execution(stop_postgres_instance,
                                               exploration_process)
    print("Exploration postgres killed successfully")
    _, pgdata_remove_time = timed_execution(execute_in_container, EXPLORATION,
                                            f"sudo rm -rf {PGDATA2_LOC}/*")
    print("Killing exploration container")
    _, docker_teardown_time = timed_execution(shutdown_exploratory_docker,
                                              exploratory_container)
    print("Exploration container killed")
    _, snapshot_destroy_time = timed_execution(destroy_exploratory_data_cow)
    teardown_time = postgres_stop_time_ns + pgdata_remove_time + docker_teardown_time + snapshot_destroy_time

    return checkpoint_time_ns, copy_time_ns, docker_start_time_ns, reset_wal_time, postgres_startup_time, teardown_time, valid


def collect_results(result_file: str, benchbase_proc: subprocess.Popen):
    # Incrementally write to file so we don't lose data in case of runtime failure
    with open(result_file, "w") as f:
        i = 0
        # TODO find out cleaner way to write json
        f.write("[\n")
        first_obj = True
        while benchbase_proc.poll() is None:
            checkpoint_time_ns, copy_time_ns, docker_startup_time_ns, reset_wal_time_ns, postgres_startup_time_ns, teardown_time_ns, valid = test_copy()
            if not first_obj:
                f.write(",\n")
            f.write("\t{\n")
            f.write(f'\t\t"iteration": {i},\n')
            f.write(f'\t\t"checkpoint_time_ns": {checkpoint_time_ns},\n')
            f.write(f'\t\t"copy_time_ns": {copy_time_ns},\n')
            f.write(
                f'\t\t"docker_startup_time_ns": {docker_startup_time_ns},\n')
            f.write(
                f'\t\t"reset_wal_time_ns": {reset_wal_time_ns},\n')
            f.write(
                f'\t\t"postgres_startup_time_ns": {postgres_startup_time_ns},\n')
            f.write(f'\t\t"teardown_time_ns": {teardown_time_ns},\n')
            f.write(f'\t\t"valid": {"true" if valid else "false"}\n')
            f.write("\t}")
            i += 1
            first_obj = False
        f.write("\n")
        f.write("]\n")


def main():
    print("Set up Docker environment")
    setup_docker_env()
    print("Docker environment set up")

    print("Starting Docker containers")
    docker_process = start_replication_docker()
    wait_for_pg_ready(PRIMARY, PRIMARY_PORT, docker_process)
    wait_for_pg_ready(REPLICA, PRIMARY_PORT, docker_process)
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

    benchbase_proc = run_benchbase(create=False, load=False, execute=True,
                                   block=False,
                                   output_strategy=OutputStrategy.Hide)

    collect_results(result_file, benchbase_proc)

    cleanup_benchbase()
    print("Killing Docker containers")
    shutdown_replication_docker(docker_process)
    print("Docker containers killed successfully")


if __name__ == "__main__":
    main()
