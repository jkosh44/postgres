# COW Test

## Description
1. Copy the `pgdata` of a running postgres replica instance.
2. Time how long the copy takes.
3. Start a primary instance using the copied data.
4. See if primary instance is valid.

## Executing
MAKE SURE you do the following before testing:
1. sudo docker volume create pgdata
2. sudo docker volume create pgdata2
3. sudo chown -R 1000:1000 /var/lib/docker/volumes/pgdata
4. sudo chown -R 1000:1000 /var/lib/docker/volumes/pgdata2
5. Link those directories in `docker-compose-replication.yml` under `volumes`
6. enable docker `sudo systemctl start docker`
7. Configure docker to use a proxy: https://stackoverflow.com/questions/23111631/cannot-download-docker-images-behind-a-proxy
8. sudo docker-compose -f ./cmudb/env/docker-compose-replication.yml down --volumes
9. sudo docker volume rm pgdata
10. sudo docker volume rm pgdata2
    docker rm $(docker ps -aq)

## ZFS
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

Inspect disks: `sudo fdisk -l`

ziffean skew is YCSB
come up with degenerative case
    Uniform distribution (see if ycsb has parameter)
Check restartpoints in logs
Deliverable: Build deamon that takes commands and can do exploration shit
Wan is doing machine learning side of things
Final experiment
    Given a postgres query trace replay trace in exploratory instance (pg_replay)
    For the entire experiment have line graph of replica replay with vertical line of exploratory events
    End to end experiment is what I should sell


## Exploration ideas
- Throw out logs after checkpoints
- Try larger DBs
- Am I pinging is_ready too much?

Get disk usage: `iostat -xd 1`

Look at: /etc/postgresql/12/main/pg_hba.conf, do we need to copy this?