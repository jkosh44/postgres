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