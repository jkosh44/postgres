# COW Test

## Description
1. Copy the `pgdata` of a running postgres replica instance.
2. Time how long the copy takes.
3. Start a primary instance using the copied data.
4. See if primary instance is valid.

## Data
Using YCSB Update only to load data before the copy, and update data during the copy.
### Data Size (by scalefactor)
- **1:**
```
7.3M    /pgdata/base/12660
7.3M    /pgdata/base/12659
8.5M    /pgdata/base/16385
7.3M    /pgdata/base/1
31M     /pgdata/base
4.0K    /pgdata/pg_stat
12K     /pgdata/pg_xact
4.0K    /pgdata/pg_tblspc
4.0K    /pgdata/pg_notify
4.0K    /pgdata/pg_twophase
4.0K    /pgdata/pg_commit_ts
4.0K    /pgdata/pg_serial
4.0K    /pgdata/pg_snapshots
4.0K    /pgdata/pg_replslot
544K    /pgdata/global
4.0K    /pgdata/pg_subtrans
4.0K    /pgdata/pg_stat_tmp
4.0K    /pgdata/pg_logical/snapshots
4.0K    /pgdata/pg_logical/mappings
16K     /pgdata/pg_logical
12K     /pgdata/pg_multixact/offsets
12K     /pgdata/pg_multixact/members
28K     /pgdata/pg_multixact
4.0K    /pgdata/pg_dynshmem
4.0K    /pgdata/pg_wal/archive_status
33M     /pgdata/pg_wal
64M     /pgdata
```
- **10**:
```
7.3M    /pgdata/base/12660
7.3M    /pgdata/base/12659
19M     /pgdata/base/16385
7.3M    /pgdata/base/1
41M     /pgdata/base
4.0K    /pgdata/pg_stat
12K     /pgdata/pg_xact
4.0K    /pgdata/pg_tblspc
4.0K    /pgdata/pg_notify
4.0K    /pgdata/pg_twophase
4.0K    /pgdata/pg_commit_ts
4.0K    /pgdata/pg_serial
4.0K    /pgdata/pg_snapshots
4.0K    /pgdata/pg_replslot
544K    /pgdata/global
4.0K    /pgdata/pg_subtrans
4.0K    /pgdata/pg_stat_tmp
4.0K    /pgdata/pg_logical/snapshots
4.0K    /pgdata/pg_logical/mappings
16K     /pgdata/pg_logical
12K     /pgdata/pg_multixact/offsets
12K     /pgdata/pg_multixact/members
28K     /pgdata/pg_multixact
4.0K    /pgdata/pg_dynshmem
4.0K    /pgdata/pg_wal/archive_status
33M     /pgdata/pg_wal
74M     /pgdata
```
- **100**:
```
7.3M    /pgdata/base/12660
7.3M    /pgdata/base/12659
122M    /pgdata/base/16385
7.3M    /pgdata/base/1
144M    /pgdata/base
4.0K    /pgdata/pg_stat
12K     /pgdata/pg_xact
4.0K    /pgdata/pg_tblspc
4.0K    /pgdata/pg_notify
4.0K    /pgdata/pg_twophase
4.0K    /pgdata/pg_commit_ts
4.0K    /pgdata/pg_serial
4.0K    /pgdata/pg_snapshots
4.0K    /pgdata/pg_replslot
544K    /pgdata/global
4.0K    /pgdata/pg_subtrans
4.0K    /pgdata/pg_stat_tmp
4.0K    /pgdata/pg_logical/snapshots
4.0K    /pgdata/pg_logical/mappings
16K     /pgdata/pg_logical
12K     /pgdata/pg_multixact/offsets
12K     /pgdata/pg_multixact/members
28K     /pgdata/pg_multixact
4.0K    /pgdata/pg_dynshmem
4.0K    /pgdata/pg_wal/archive_status
129M    /pgdata/pg_wal
273M    /pgdata
```
-**1000**:
```
7.3M    /pgdata/base/12660
7.3M    /pgdata/base/12659
1.2G    /pgdata/base/16385
7.3M    /pgdata/base/1
1.2G    /pgdata/base
4.0K    /pgdata/pg_stat
12K     /pgdata/pg_xact
4.0K    /pgdata/pg_tblspc
4.0K    /pgdata/pg_notify
4.0K    /pgdata/pg_twophase
4.0K    /pgdata/pg_commit_ts
4.0K    /pgdata/pg_serial
4.0K    /pgdata/pg_snapshots
4.0K    /pgdata/pg_replslot
544K    /pgdata/global
44K     /pgdata/pg_subtrans
4.0K    /pgdata/pg_stat_tmp
4.0K    /pgdata/pg_logical/snapshots
4.0K    /pgdata/pg_logical/mappings
16K     /pgdata/pg_logical
12K     /pgdata/pg_multixact/offsets
12K     /pgdata/pg_multixact/members
28K     /pgdata/pg_multixact
4.0K    /pgdata/pg_dynshmem
4.0K    /pgdata/pg_wal/archive_status
1.1G    /pgdata/pg_wal
2.2G    /pgdata/
```
- **10000**:
```
7.3M    /pgdata/base/12660
7.3M    /pgdata/base/12659
12G     /pgdata/base/16385
7.3M    /pgdata/base/1
12G     /pgdata/base
4.0K    /pgdata/pg_stat
28K     /pgdata/pg_xact
4.0K    /pgdata/pg_tblspc
4.0K    /pgdata/pg_notify
4.0K    /pgdata/pg_twophase
4.0K    /pgdata/pg_commit_ts
4.0K    /pgdata/pg_serial
4.0K    /pgdata/pg_snapshots
4.0K    /pgdata/pg_replslot
544K    /pgdata/global
44K     /pgdata/pg_subtrans
4.0K    /pgdata/pg_stat_tmp
4.0K    /pgdata/pg_logical/snapshots
4.0K    /pgdata/pg_logical/mappings
16K     /pgdata/pg_logical
12K     /pgdata/pg_multixact/offsets
12K     /pgdata/pg_multixact/members
28K     /pgdata/pg_multixact
4.0K    /pgdata/pg_dynshmem
4.0K    /pgdata/pg_wal/archive_status
1.1G    /pgdata/pg_wal
13G     /pgdata
```

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