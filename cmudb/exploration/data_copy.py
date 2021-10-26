from util import execute_sys_command, ZFS_SNAPSHOT_NAME, EXPLORATION_VOLUME_POOL


# ZFS Functionality

def zfs_create_snapshot(zfs_pool: str, snapshot_name: str):
    execute_sys_command(f"sudo zfs snapshot {zfs_pool}@{snapshot_name}")


def zfs_destroy_snapshot(zfs_snapshot: str):
    execute_sys_command(f"sudo zfs destroy {zfs_snapshot}")


def zfs_clone_snapshot(zfs_snapshot: str, clone_pool_name: str):
    execute_sys_command(f"sudo zfs clone {zfs_snapshot} {clone_pool_name}")


def zfs_destroy_pool(pool_name: str):
    execute_sys_command(f"sudo zfs destroy {pool_name}")


# Exploratory Data

def copy_pgdata_cow(zfs_volume_pool: str, zfs_replica_pool: str):
    zfs_create_snapshot(f"{zfs_volume_pool}/{zfs_replica_pool}", ZFS_SNAPSHOT_NAME)
    zfs_clone_snapshot(f"{zfs_volume_pool}/{zfs_replica_pool}@{ZFS_SNAPSHOT_NAME}",
                       f"{zfs_volume_pool}/{EXPLORATION_VOLUME_POOL}")


def destroy_exploratory_data_cow(zfs_volume_pool: str, zfs_replica_pool: str):
    zfs_destroy_pool(f"{zfs_volume_pool}/{EXPLORATION_VOLUME_POOL}")
    zfs_destroy_snapshot(f"{zfs_volume_pool}/{zfs_replica_pool}@{ZFS_SNAPSHOT_NAME}")
