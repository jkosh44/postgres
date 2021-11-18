import datetime
import subprocess
import time
from threading import Thread
from typing import Tuple, Union

from benchbase import cleanup_benchbase, run_benchbase, setup_benchbase
from data_copy import copy_pgdata_cow, destroy_exploratory_data_cow
from pgnp_docker import start_replication_docker, shutdown_replication_docker, \
    execute_in_container, \
    start_exploration_docker, \
    shutdown_exploratory_docker, setup_docker_env
from sql import execute_sql, start_and_wait_for_postgres_instance, stop_postgres_instance, \
    wait_for_pg_ready, reset_wal
from util import PGDATA_LOC, EXPLORATION_PORT, \
    OutputStrategy, PRIMARY_PORT, EXPLORATION, \
    REPLICA, PRIMARY, stop_process

SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60
MICROSECOND_PER_SECOND = 1000000


def start_exploratory() -> Tuple[bool, Union[subprocess.Popen, None], Union[subprocess.Popen, None]]:
    print("Copying replica data")
    copy_pgdata_cow()
    print("Exploration data copied")
    print("Starting exploration container")
    exploratory_container = start_exploration_docker()
    if exploratory_container.returncode is not None:
        print("Failed to start exploration container, cleaning up env")
        shutdown_exploratory_docker(exploratory_container)
        destroy_exploratory_data_cow()
        return False, None, None
    execute_in_container(EXPLORATION,
                         f"sudo chown terrier:terrier -R {PGDATA_LOC}")
    execute_in_container(EXPLORATION, f"sudo chmod 700 -R {PGDATA_LOC}")
    execute_in_container(EXPLORATION, f"rm {PGDATA_LOC}/postmaster.pid")
    execute_in_container(EXPLORATION, f"rm {PGDATA_LOC}/standby.signal")
    print("Exploration container started")
    print("Starting exploration postgres instance")
    reset_wal(EXPLORATION)
    exploration_process, valid = start_and_wait_for_postgres_instance(EXPLORATION, EXPLORATION_PORT)
    if not valid:
        print("Failed to start exploration postgres instance, cleaning up env")
        stop_postgres_instance(exploration_process)
        shutdown_exploratory_docker(exploratory_container)
        destroy_exploratory_data_cow()
        return False, None, None
    print("Exploration postgres instance started")
    return True, exploration_process, exploratory_container


def stop_exploratory(exploration_process: subprocess.Popen, exploratory_container: subprocess.Popen):
    # Shutdown exploration instance
    print("Killing exploration postgres process")
    stop_postgres_instance(exploration_process)
    print("Exploration postgres killed successfully")
    print("Killing exploration container")
    shutdown_exploratory_docker(exploratory_container)
    print("Exploration container killed")
    destroy_exploratory_data_cow()


def main():
    sleep_time_sec = 60 * 1

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

    setup_benchbase()
    print("Loading data")
    run_benchbase(create=True, load=True, execute=False)
    print("Data loaded")

    test_time = time.time()

    lag_thread = Thread(target=collect_replica_lag, args=(test_time,))
    lag_thread.start()

    benchbase_proc = run_benchbase(create=False, load=False, execute=True, block=False,
                                   output_strategy=OutputStrategy.Hide)

    time.sleep(sleep_time_sec)

    valid, exploration_process, exploratory_container = start_exploratory()

    exploratory_benchbase_proc = None
    if valid:
        with open(f"exploratory_time_{test_time}", "w") as f:
            f.write(str(time.time_ns()))
        exploratory_benchbase_proc = run_benchbase(create=True, load=True, execute=True, block=False,
                                                   output_strategy=OutputStrategy.Hide)
        time.sleep(sleep_time_sec)

    print("Joining threads")
    global done
    done = True
    lag_thread.join()
    print("Threads joined")

    stop_process(benchbase_proc)
    if exploratory_benchbase_proc is not None:
        stop_process(exploratory_benchbase_proc)

    cleanup_benchbase()
    print("Killing Docker containers")
    shutdown_replication_docker(docker_process)
    print("Docker containers killed successfully")


def collect_replica_lag(test_time: float):
    with open(f"replica_lag_{test_time}.json", "w") as f:
        f.write("[\n")
        first_obj = True
        while not done:
            start_time = time.time_ns()
            replica_lag = execute_sql("SELECT replay_lag FROM pg_stat_replication", PRIMARY_PORT)
            if len(replica_lag) == 0:
                replica_lag = 0
            else:
                replica_lag = replica_lag[0]
                replica_time = datetime.datetime.strptime(replica_lag, "%H:%M:%S.%f")
                replica_lag = (replica_time.hour * SECONDS_PER_HOUR) + (
                        replica_time.minute * SECONDS_PER_MINUTE) + replica_time.second + (
                                      replica_time.microsecond / MICROSECOND_PER_SECOND)

            if not first_obj:
                f.write(",\n")
                first_obj = False
            f.write("\t{\n")
            f.write(f'\t\t"time": {start_time},\n')
            f.write(f'\t\t"replica_lag": {replica_lag}\n')
            f.write("\t}")
            f.flush()
            time.sleep(5)

        f.write("\n")
        f.write("]\n")


done = False

if __name__ == "__main__":
    main()
