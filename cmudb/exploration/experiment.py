import subprocess
import time
from functools import reduce
from threading import Thread
from typing import Tuple

from benchbase import cleanup_benchbase, run_benchbase, setup_benchbase
from data_copy import copy_pgdata_cow, destroy_exploratory_data_cow
from pgnp_docker import start_replication_docker, shutdown_replication_docker, \
    execute_in_container, \
    start_exploration_docker, \
    shutdown_exploratory_docker, setup_docker_env, get_pg_data_size
from sql import execute_sql, validate_sql_results, validate_table_is_not_empty, \
    checkpoint, \
    start_and_wait_for_postgres_instance, stop_postgres_instance, \
    wait_for_pg_ready, reset_wal
from util import PGDATA_LOC, EXPLORATION_PORT, \
    OutputStrategy, PRIMARY_PORT, EXPLORATION, \
    timed_execution, REPLICA, PRIMARY, REPLICA_PORT, execute_sys_command, UTF_8

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
                   [validate_table_is_not_empty(table, EXPLORATION_PORT) for table
                    in tables])


def test_copy() -> Tuple[int, int, int, int, int, int, bool, str, int, int]:
    # Start exploration instance
    print("Taking checkpoint")
    precheckpoint_dirty_pages = execute_sql("SELECT COUNT(*) FROM pg_buffercache WHERE isdirty != 'f'", REPLICA_PORT)
    if len(precheckpoint_dirty_pages) > 0:
        precheckpoint_dirty_pages = int(precheckpoint_dirty_pages[0])
    else:
        precheckpoint_dirty_pages = 0

    _, checkpoint_time_ns = timed_execution(checkpoint, REPLICA_PORT)

    postcheckpoint_dirty_pages = execute_sql("SELECT COUNT(*) FROM pg_buffercache WHERE isdirty != 'f'", REPLICA_PORT)
    if len(postcheckpoint_dirty_pages) > 0:
        postcheckpoint_dirty_pages = int(postcheckpoint_dirty_pages[0])
    else:
        postcheckpoint_dirty_pages = 0
    print("Checkpoint complete")
    print("Copying replica data")
    _, copy_time_ns = timed_execution(copy_pgdata_cow)
    print("Exploration data copied")
    print("Starting exploration container")
    exploratory_container, docker_start_time_ns = timed_execution(
        start_exploration_docker)
    if exploratory_container.returncode is not None:
        print("Failed to start exploration container, cleaning up env")
        ret_code = exploratory_container.returncode
        shutdown_exploratory_docker(exploratory_container)
        destroy_exploratory_data_cow()
        return checkpoint_time_ns, copy_time_ns, docker_start_time_ns, 0, 0, 0, False, \
               f"Container failed to start, return code {ret_code}", precheckpoint_dirty_pages, postcheckpoint_dirty_pages
    execute_in_container(EXPLORATION,
                         f"sudo chown terrier:terrier -R {PGDATA_LOC}")
    execute_in_container(EXPLORATION, f"sudo chmod 700 -R {PGDATA_LOC}")
    execute_in_container(EXPLORATION, f"rm {PGDATA_LOC}/postmaster.pid")
    execute_in_container(EXPLORATION, f"rm {PGDATA_LOC}/standby.signal")
    print("Exploration container started")
    print("Starting exploration postgres instance")
    _, reset_wal_time = timed_execution(reset_wal, EXPLORATION)
    # reset_wal_time = 0
    (exploration_process, valid), postgres_startup_time = timed_execution(
        start_and_wait_for_postgres_instance, EXPLORATION,
        EXPLORATION_PORT)
    if not valid:
        print("Failed to start exploration postgres instance, cleaning up env")
        ret_code = exploration_process.returncode
        stop_postgres_instance(exploration_process)
        shutdown_exploratory_docker(exploratory_container)
        destroy_exploratory_data_cow()
        return checkpoint_time_ns, copy_time_ns, docker_start_time_ns, reset_wal_time, postgres_startup_time, 0, valid, \
               f"Postgres failed to start, return code {ret_code}", precheckpoint_dirty_pages, postcheckpoint_dirty_pages
    print("Exploration postgres instance started")

    # Validate exploration instance
    print("Validating data")
    valid = validate_exploration_process()
    print("Done validating data")

    # Shutdown exploration instance
    print("Killing exploration postgres process")
    _, postgres_stop_time_ns = timed_execution(stop_postgres_instance,
                                               exploration_process)
    print("Exploration postgres killed successfully")
    print("Killing exploration container")
    _, docker_teardown_time = timed_execution(shutdown_exploratory_docker,
                                              exploratory_container)
    print("Exploration container killed")
    _, snapshot_destroy_time = timed_execution(destroy_exploratory_data_cow)
    teardown_time = postgres_stop_time_ns + docker_teardown_time + snapshot_destroy_time

    return checkpoint_time_ns, copy_time_ns, docker_start_time_ns, reset_wal_time, postgres_startup_time, teardown_time, valid, "" if valid else "Data lost", precheckpoint_dirty_pages, postcheckpoint_dirty_pages


def collect_results(result_file: str):
    # Incrementally write to file so we don't lose data in case of runtime failure
    with open(result_file, "w") as f:
        global_iteration = 0
        # TODO find out cleaner way to write json
        f.write("[\n")
        first_obj = True

        for benchbase_iteration in range(2):
            benchbase_proc = run_benchbase(create=False, load=False, execute=True,
                                           block=False,
                                           output_strategy=OutputStrategy.Capture)

            for line in iter(lambda: benchbase_proc.stdout.readline(), b''):
                if isinstance(line, bytes):
                    line = line.decode(UTF_8)
                print(line, end="")
                if "Warmup complete, starting measurements" in line:
                    break

            print_thread = Thread(target=print_benchbase_output, args=(benchbase_proc,))
            print_thread.start()

            while benchbase_proc.poll() is None:
                print(f"benchbase poll: {benchbase_proc.poll()}")
                start_time = time.time_ns()
                checkpoint_time_ns, copy_time_ns, docker_startup_time_ns, reset_wal_time_ns, postgres_startup_time_ns, teardown_time_ns, valid, error_msg, precheckpoint_dirty_pages, postcheckpoint_dirty_pages = test_copy()
                if not first_obj:
                    f.write(",\n")
                f.write("\t{\n")
                f.write(f'\t\t"global_iteration": {global_iteration},\n')
                f.write(f'\t\t"benchbase_iteration": {benchbase_iteration},\n')
                f.write(f'\t\t"start_time_ns": {start_time},\n')
                f.write(f'\t\t"precheckpoint_dirty_pages": {precheckpoint_dirty_pages},\n')
                f.write(f'\t\t"checkpoint_time_ns": {checkpoint_time_ns},\n')
                f.write(f'\t\t"postcheckpoint_dirty_pages": {postcheckpoint_dirty_pages},\n')
                f.write(f'\t\t"copy_time_ns": {copy_time_ns},\n')
                f.write(
                    f'\t\t"docker_startup_time_ns": {docker_startup_time_ns},\n')
                f.write(
                    f'\t\t"reset_wal_time_ns": {reset_wal_time_ns},\n')
                f.write(
                    f'\t\t"postgres_startup_time_ns": {postgres_startup_time_ns},\n')
                f.write(f'\t\t"teardown_time_ns": {teardown_time_ns},\n')
                f.write(f'\t\t"valid": {"true" if valid else "false"},\n')
                f.write(f'\t\t"error": "{error_msg}"\n')
                f.write("\t}")
                f.flush()
                global_iteration += 1
                first_obj = False

            print_thread.join()
            time.sleep(60 * 15)

        f.write("\n")
        f.write("]\n")


def main():
    print("Set up Docker environment")
    setup_docker_env()
    print("Docker environment set up")

    print("Clean any existing ZFS snapshots and clones")
    destroy_exploratory_data_cow()
    print("Existing ZFS snapshots and clones cleaned")

    print("Starting Docker containers")
    docker_process = start_replication_docker()
    wait_for_pg_ready(PRIMARY, PRIMARY_PORT, docker_process)
    wait_for_pg_ready(REPLICA, PRIMARY_PORT, docker_process)
    print("Docker containers started successfully")

    execute_sql("ALTER SYSTEM SET log_min_error_statement TO 'FATAL';", 15721)
    execute_sql("ALTER SYSTEM SET log_min_error_statement TO 'FATAL';", 15722)
    execute_sql("CREATE EXTENSION pg_buffercache;", 15721)
    execute_sql("CREATE EXTENSION pg_buffercache;", 15722)

    # Load some data into primary for validation
    load_validation_data()

    setup_benchbase()
    print("Loading data")
    run_benchbase(create=True, load=True, execute=False)
    print("Data loaded")

    test_time = time.time()
    result_file = RESULT_FILE.format(test_time)
    db_size = get_pg_data_size(REPLICA)
    result_file = f"{result_file}_{db_size}"

    io_thread = Thread(target=collect_io_stats, args=(test_time,))
    ssd_thread = Thread(target=collect_ssd_stats, args=(test_time,))
    dstat_thread = Thread(target=collect_dstat, args=(test_time,))

    io_thread.start()
    ssd_thread.start()
    dstat_thread.start()

    collect_results(result_file)

    global done
    done = True
    io_thread.join()
    ssd_thread.join()
    dstat_thread.join()

    # throughput = get_benchbase_throughput(benchbase_proc)
    # print(f"Saving throughput {throughput}")
    # result_throughput_file = f"{result_file}.throughput"
    # with open(result_throughput_file, "w") as f:
    #     f.write(f"{throughput}\n")
    # print("Throughput saved")

    cleanup_benchbase()
    print("Killing Docker containers")
    shutdown_replication_docker(docker_process)
    print("Docker containers killed successfully")


def collect_io_stats(test_time: float):
    with open(f"iostats_{test_time}", "w") as f:
        while not done:
            start_time = time.time_ns()
            _, out, _ = execute_sys_command("iostat -x", output_strategy=OutputStrategy.Capture, block=True)
            f.write(f"Time: {start_time}\n")
            f.write(f"{out}\n\n")
            f.flush()
            time.sleep(10)


def collect_ssd_stats(test_time: float):
    with open(f"ssdstats_{test_time}", "w") as f:
        while not done:
            start_time = time.time_ns()
            _, out, _ = execute_sys_command("sudo nvme smart-log /dev/nvme0n1", output_strategy=OutputStrategy.Capture,
                                            block=True)
            f.write(f"Time: {start_time}\n")
            f.write(f"{out}\n\n")
            f.flush()
            time.sleep(10)


def print_benchbase_output(benchbase_proc: subprocess.Popen):
    while benchbase_proc.poll() is None:
        for line in iter(lambda: benchbase_proc.stdout.readline(), b''):
            if isinstance(line, bytes):
                line = line.decode(UTF_8)
            print(line, end="")


def collect_dstat(test_time: float):
    with open(f"dstat_{test_time}", "w") as f:
        while not done:
            start_time = time.time_ns()
            _, out, _ = execute_sys_command(f"sudo dstat --noupdate -amst 1 1", output_strategy=OutputStrategy.Capture,
                                            block=True)
            f.write(f"Time: {start_time}\n")
            f.write(f"{out}\n\n")
            f.flush()
            time.sleep(10)


done = False

if __name__ == "__main__":
    main()