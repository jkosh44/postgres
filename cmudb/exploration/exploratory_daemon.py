import argparse
import subprocess
from typing import Tuple

from data_copy import copy_pgdata_cow, destroy_exploratory_data_cow
from pgnp_docker import start_exploration_docker, execute_in_container, shutdown_exploratory_docker, setup_docker_env
from sql import checkpoint, reset_wal, start_and_wait_for_postgres_instance, stop_postgres_instance, execute_sql
from util import ZFS_DOCKER_VOLUME_POOL, REPLICA_VOLUME_POOL, REPLICA_PORT, EXPLORATION_PORT, \
    EXPLORATION_CONTAINER_NAME, \
    PGDATA_LOC, DOCKER_VOLUME_DIR


def main():
    aparser = argparse.ArgumentParser(description="Exploratory Daemon")
    # postgres args
    aparser.add_argument("--postgres-replica-port", help="Port that replica instance is running on",
                         default=REPLICA_PORT)
    aparser.add_argument("--postgres-exploratory-port", help="Port that exploratory instance will run on",
                         default=EXPLORATION_PORT)
    # ZFS args
    aparser.add_argument("--zfs-volume-pool", help="ZFS pool name for docker volume directory",
                         default=ZFS_DOCKER_VOLUME_POOL)
    aparser.add_argument("--zfs-replica-pool-name", help="Relative name of ZFS pool used for the replica volume",
                         default=REPLICA_VOLUME_POOL)
    # Docker args
    aparser.add_argument("docker-volume-directory", help="directory path of the docker volume directory",
                         default=DOCKER_VOLUME_DIR)
    args = vars(aparser.parse_args())

    run_daemon(args["postgres-replica-port"], args["postgres-exploratory-port"], args["zfs_volume_pool"],
               args["zfs_replica_pool"], args["docker_volume_directory"])


def run_daemon(replica_port: int, exploratory_port: int, zfs_volume_pool: str, zfs_replica_pool: str,
               docker_volume_dir: str):
    setup_docker_env(docker_volume_dir)
    docker_proc, postgres_proc = spin_up_exploratory_instance(replica_port, exploratory_port, zfs_volume_pool, zfs_replica_pool, docker_volume_dir)
    execute_sql("CREATE TABLE foo(a int);", EXPLORATION_PORT)
    execute_sql("INSERT INTO foo VALUES (42), (666);", EXPLORATION_PORT)
    execute_sql("SELECT * FROM foo;", EXPLORATION_PORT)
    spin_down_exploratory_instance(docker_proc, postgres_proc, zfs_volume_pool, zfs_replica_pool, docker_volume_dir)


def spin_up_exploratory_instance(replica_port: int, exploratory_port: int, zfs_volume_pool: str, zfs_replica_pool: str,
                                 docker_volume_dir: str) -> Tuple[subprocess.Popen, subprocess.Popen]:
    checkpoint(replica_port)
    copy_pgdata_cow(zfs_volume_pool, zfs_replica_pool)
    # TODO can combine the rest in entry script
    docker_proc = start_exploration_docker(docker_volume_dir)
    execute_in_container(EXPLORATION_CONTAINER_NAME,
                         f"sudo chown terrier:terrier -R {PGDATA_LOC}")
    execute_in_container(EXPLORATION_CONTAINER_NAME, f"sudo chmod 700 -R {PGDATA_LOC}")
    execute_in_container(EXPLORATION_CONTAINER_NAME, f"rm {PGDATA_LOC}/postmaster.pid")
    execute_in_container(EXPLORATION_CONTAINER_NAME, f"rm {PGDATA_LOC}/standby.signal")
    reset_wal(EXPLORATION_CONTAINER_NAME)
    postgres_proc, valid = start_and_wait_for_postgres_instance(EXPLORATION_CONTAINER_NAME, exploratory_port)
    # TODO handle invalid
    return docker_proc, postgres_proc


def spin_down_exploratory_instance(docker_proc: subprocess.Popen, postgres_proc: subprocess.Popen, zfs_volume_pool: str,
                                   zfs_replica_pool: str, docker_volume_dir: str):
    stop_postgres_instance(postgres_proc)
    shutdown_exploratory_docker(docker_proc, docker_volume_dir)
    destroy_exploratory_data_cow(zfs_volume_pool, zfs_replica_pool)


if __name__ == '__main__':
    main()
