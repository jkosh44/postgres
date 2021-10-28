# Paper outline

## Last Semester
TODO

## This Semester

### Motivations
TODO

### Hypothesis
- Replica under utilized, we can explore without affecting replication lag

### Results
- COW
- COW with checkpoint
- COW with pg_resetwal
- COW with checkpoint and pg_resetwal
  - Various sizez 
- EXT4
- EXT4 with checkpoint
- EXT4 with pg_resetwal
- EXT4 with checkpoint and pg_resetwal
- Replay lag y axis, x-axis is time. Create exploration and run benchbase
- Page cache experiment:
  - Load DB
  - call pg_warm
  - SELECT * FROM table
  - Create exploration instance
  - call pg_warm in container
  - 0% hit in BPM
  - 100% hit rate in OS page cache
  - Discuss what would happen without OS page cache (we'd have more misses in exploratory)

#### Reset WAL
`pg_resetwal`: https://www.postgresql.org/docs/13/app-pgresetwal.html

**Replica Count**: 10000000
**Exploratory Count**: 9968874
Loss = (10000000 - 9968874)/10000000 = 0.0031126

- TODO find detailed explanation

### Related work
- DB Lab
  - Not online
  - Also uses ZFS
- Aurora Snapshot
  - TODO
- Scaling Distributed Machine Learning with the Parameter Server
  - Stale data is OK for ML
  - TODO