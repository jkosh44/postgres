from util import execute_sys_command

ZFS_POOL_ROOT = "zpool-docker/volumes"
REPLICA_POOL = "pgdata-replica"
EXPLORATION_POOL = "pgdata-exploration"
SNAPSHOT_NAME = "explore"


def zfs_create_snapshot(zfs_pool: str, snapshot_name: str):
    execute_sys_command(f"sudo zfs snapshot {zfs_pool}@{snapshot_name}")


def zfs_destroy_snapshot(zfs_snapshot: str):
    execute_sys_command(f"sudo zfs destroy {zfs_snapshot}")


def zfs_clone_snapshot(zfs_snapshot: str, clone_pool_name: str):
    execute_sys_command(f"sudo zfs clone {zfs_snapshot} {clone_pool_name}")


def zfs_destroy_pool(pool_name: str):
    execute_sys_command(f"sudo zfs destroy {pool_name}")


def copy_pgdata_cow():
    zfs_create_snapshot(f"{ZFS_POOL_ROOT}/{REPLICA_POOL}", SNAPSHOT_NAME)
    zfs_clone_snapshot(f"{ZFS_POOL_ROOT}/{REPLICA_POOL}@{SNAPSHOT_NAME}", f"{ZFS_POOL_ROOT}/{EXPLORATION_POOL}")


def destroy_exploratory_data_cow():
    zfs_destroy_pool(f"{ZFS_POOL_ROOT}/{EXPLORATION_POOL}")
    zfs_destroy_snapshot(f"{ZFS_POOL_ROOT}/{REPLICA_POOL}@{SNAPSHOT_NAME}")
