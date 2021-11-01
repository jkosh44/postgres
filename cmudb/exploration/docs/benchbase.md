## Data
Using YCSB Update only to load data before the copy, and update data during the copy.
`du -h /pgdata`
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
-**1,000**:
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
- **10,000**:
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

- **100,000**
21K     /pgdata/pg_stat_tmp
512     /pgdata/pg_stat
9.0K    /pgdata/pg_multixact/members
9.0K    /pgdata/pg_multixact/offsets
19K     /pgdata/pg_multixact
113G    /pgdata/base/16385
8.5M    /pgdata/base/12660
8.2M    /pgdata/base/12659
8.2M    /pgdata/base/1
113G    /pgdata/base
259K    /pgdata/pg_subtrans
591K    /pgdata/global
512     /pgdata/pg_commit_ts
259K    /pgdata/pg_xact
512     /pgdata/pg_logical/mappings
512     /pgdata/pg_logical/snapshots
2.5K    /pgdata/pg_logical
512     /pgdata/pg_tblspc
512     /pgdata/pg_notify
512     /pgdata/pg_serial
512     /pgdata/pg_wal/archive_status
1.1G    /pgdata/pg_wal
512     /pgdata/pg_twophase
512     /pgdata/pg_replslot
512     /pgdata/pg_snapshots
512     /pgdata/pg_dynshmem
114G    /pgdata/


[WARN ] 2021-10-31 20:53:48,507 [YCSBWorker<008>]  com.oltpbenchmark.api.Worker doWork - SQLException occurr
ed during [com.oltpbenchmark.benchmarks.ycsb.procedures.UpdateRecord/01] and will not be retried... sql stat
e [53200], error code [0].                                                                                  
org.postgresql.util.PSQLException: ERROR: out of shared memory                                              
  Hint: You might need to increase max_pred_locks_per_transaction. 