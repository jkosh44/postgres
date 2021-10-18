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
1. Create Docker zpool for docker (replica/exploration): `sudo zpool create -f zpool-docker -m /mnt/docker /dev/nvme0n1`
2. Create Docker zpool for primary: `sudo zpool create -f zpool-primary -m /mnt/pgprimary /dev/nvme1n1`
3. Create filesystem for docker volumes: 
```bash
sudo zfs create zpool-docker/volumes
sudo zfs create zpool-docker/volumes/pgdata-primary
sudo zfs create zpool-docker/volumes/pgdata-replica
```
4. Create file system for primary: `sudo zfs create zpool-primary/pgdata`
5. Create symbolic link from docker volumes directory to primary disk: `sudo ln -s /mnt/pgprimary/pgdata /mnt/docker/volumes/pgdata-primary`
6. Create pgdata-primary volume:
```bash
sudo docker volume create pgdata-primary
sudo chown -R 1000:1000 /mnt/docker/volumes/pgdata-primary
```
7. Create pgdata-replica volume:
```bash
sudo docker volume create pgdata-primary
sudo chown -R 1000:1000 /mnt/docker/volumes/pgdata-primary
```
9. Make network tombstone to prevent getting locked out of network: `sudo docker network create --driver=bridge --subnet 172.19.253.0/30 tombstone`
10. Start primary and replica containers using compose: `sudo docker-compose -p replication -f cmudb/env/docker-compose-replication.yml up`
11. (Optional) Run benchbase against primary
12. Snapshot replica: `sudo zfs snapshot zpool-docker/volumes/pgdata-replica@explore`
13. Clone replica to exploratory: `sudo zfs clone zpool-docker/volumes/pgdata-replica@explore zpool-docker/volumes/pgdata-exploration`
14. Create exploratory volume: `sudo docker volume create pgdata-exploration`
15. Create exploratory container using compose: `sudo docker-compose -p exploratory -f cmudb/env/docker-compose-exploration.yml up`
16. Start postgres: `docker exec exploration -c '/home/terrier/repo/build/bin/postgres -D /pgdata -p 42666'`

## Database Lab
Creates copies of postgres databases: https://postgres.ai/docs/database-lab 
- **Thin Clone**: Uses ZFS to create a snapshot 
- https://postgres.ai/docs/tutorials/database-lab-tutorial#need-to-start-over-here-is-how-to-clean-up
- `export DBLAB_DISK="/dev/nvme0n1"`