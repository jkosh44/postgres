# ZFS

```
pdladmin@dev8:~$ lsblk -l -o+MODEL
NAME    MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT MODEL
sda       8:0    0 223.6G  0 disk            Micron_5300_MTFDDAV240TDU
sda1      8:1    0   512M  0 part /boot/efi
sda2      8:2    0     1K  0 part
sda5      8:5    0 223.1G  0 part /
nvme1n1 259:0    0 894.3G  0 disk            SAMSUNG MZQLB960HAJR-00007
nvme0n1 259:1    0 465.8G  0 disk /mnt       Samsung SSD 970 EVO Plus 500GB
```

the one I added is now called `nvme0n1`

sudo fdisk -l

## Commands

`sudo zfs list -r`: List all pools
`sudo zfs list -t snapshot`: List all snapshots
`sudo zfs create pool/path`: Create new pool
`sudo zfs snapshot pool/path@snapshot-name`: Create a snapshot
`sudo zfs clone pool/path@snapshot-name pool/clone/path`: Create a pool that's a
clone of snapshot
`sudo zfs destroy object`: Destroy pool or snapshot

## Process
https://docs.docker.com/storage/storagedriver/zfs-driver/
1. Create Docker zpool: `sudo zpool create -f zpool-docker -m /mnt/docker /dev/nvme0n1`
2. Create filesystem: 
```bash
sudo zfs create zpool-docker/volumes
sudo zfs create zpool-docker/volumes/pgdata-primary
sudo zfs create zpool-docker/volumes/pgdata-replica
```
3. Create pgdata-primary volume
4. Create pgdata-replica volume
5. Start primary and replica containers using compose
????
6. Snapshot replica: `sudo zfs snapshot zpool-docker/volumes/pgdata-replica@explore`
7. Clone replica to exploratory: `sudo zfs clone zpool-docker/volumes/pgdata-replica@explore zpool-docker/volumes/pgdata-exploration`
8. Create exploratory volume: `sudo docker volume create pgdata-exploration`
9. Create exploratory container
10. Start postgres

## Database Lab
Creates copies of postgres databases: https://postgres.ai/docs/database-lab 
- **Thin Clone**: Uses ZFS to create a snapshot 
- https://postgres.ai/docs/tutorials/database-lab-tutorial#need-to-start-over-here-is-how-to-clean-up
- `export DBLAB_DISK="/dev/nvme0n1"`