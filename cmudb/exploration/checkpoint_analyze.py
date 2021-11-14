import datetime
import re

import pandas as pd
from matplotlib import pyplot as plt

CHECKPOINT_TIME_NS = "checkpoint_time_ns"
CHECKPOINT_TIME = "checkpoint_time"
PRECHECKPOINT_DIRTY_PAGE = "precheckpoint_dirty_pages"
POSTCHECKPOINT_DIRTY_PAGE = "postcheckpoint_dirty_pages"
START_TIME_NS = "start_time_ns"
START_TIME = "start_time"
VALID = "valid"

NS_PER_SEC = 1000000000

TEST_FILE_NAME = "results/final/zfs/no_vacuum_long_checkpoint_gaps/test_result_1636683372.5605218.json_54G"
IO_FILE_NAME = "results/final/zfs/no_vacuum_long_checkpoint_gaps/iostats_1636683372.5605218"
SSD_FILE_NAME = "results/final/zfs/no_vacuum_long_checkpoint_gaps/ssdstats_1636683372.5605218"
DSTAT_FILE_NAME = "results/final/zfs/no_vacuum_long_checkpoint_gaps/dstat_1636683372.5605218"
THROUGHPUT_FILE_NAME = "results/final/zfs/no_vacuum_long_checkpoint_gaps/throughput_1636683372.5605218"
PG_REPLICA_FILE_NAME = "results/final/zfs/no_vacuum_long_checkpoint_gaps/pg_io_replica_1636683372.5605218.json"
PG_PRIMARY_FILE_NAME = "results/final/zfs/no_vacuum_long_checkpoint_gaps/pg_io_primary_1636683372.5605218.json"


def main():
    # analyze_postgres_stats_time(CHECKPOINT_TIME_NS, CHECKPOINT_TIME)
    # analyze_exploratory_stats(PRECHECKPOINT_DIRTY_PAGE)
    # analyze_exploratory_stats(POSTCHECKPOINT_DIRTY_PAGE)
    # analyze_io_stats("wkB/s")
    # analyze_io_stats("rkB/s")
    # analyze_io_stats("r_await")
    # analyze_io_stats("w_await")
    # analyze_io_stats("%util")
    # analyze_ssd_stats("temperature")
    # analyze_dstats("memory-usage", "free")
    # analyze_dstats("swap", "used")
    # analyze_dstats("total-cpu-usage", "idl")
    # analyze_postgres_process_stats(PG_REPLICA_FILE_NAME)
    analyze_postgres_process_stats(PG_PRIMARY_FILE_NAME)
    # analyze_benchbase_throughput()


def analyze_postgres_stats_time(metric_name_ns: str, metric_name_sec: str):
    measurements = [
        (metric_name_ns, metric_name_sec),
        (START_TIME_NS, START_TIME)
    ]

    df = pd.read_json(TEST_FILE_NAME)
    for ns_measurement, sec_measurement in measurements:
        df[sec_measurement] = df[ns_measurement] / NS_PER_SEC

    df.plot(x=START_TIME, y=metric_name_sec, kind="line", title=f"{metric_name_sec} (sec)")
    plt.show()


def analyze_exploratory_stats(metric_name: str):
    df = pd.read_json(TEST_FILE_NAME)
    df[START_TIME] = df[START_TIME_NS] / NS_PER_SEC

    df.plot(x=START_TIME, y=metric_name, kind="line", title=f"{metric_name}")
    plt.show()


def analyze_io_stats(metric_name: str):
    stats = []
    segment_length = 14
    with open(IO_FILE_NAME, "r") as f:
        lines = f.readlines()
        while len(lines) > 0:
            cur_lines = lines[:segment_length]

            time_line = cur_lines[0]
            time_search = re.search("Time: (\\d+)", time_line)
            time = int(time_search.group(1)) / NS_PER_SEC
            cur_lines = cur_lines[1:]

            device_offset = 0
            for line in cur_lines:
                if line.startswith("Device"):
                    break
                device_offset += 1
            cur_lines = cur_lines[device_offset:]

            device_line = cur_lines[0]
            metric_offset = 0
            for metric in device_line.split():
                if metric == metric_name:
                    break
                metric_offset += 1
            cur_lines = cur_lines[1:]

            ssd_offset = 0
            for line in cur_lines:
                if line.startswith("nvme0n1"):
                    break
                ssd_offset += 1
            cur_lines = cur_lines[ssd_offset:]

            ssd_line = cur_lines[0]
            metric = float(ssd_line.split()[metric_offset])

            stats.append((time, metric))
            lines = lines[segment_length:]

    df = pd.DataFrame(stats, columns=["Time", metric_name])
    df.plot(x="Time", y=metric_name, kind="line", title=metric_name)
    plt.show()


def analyze_ssd_stats(metric_name: str):
    stats = []
    segment_length = 27
    with open(SSD_FILE_NAME, "r") as f:
        lines = f.readlines()
        while len(lines) > 0:
            cur_lines = lines[:segment_length]

            time_line = cur_lines[0]
            time_search = re.search("Time: (\\d+)", time_line)
            time = int(time_search.group(1)) / NS_PER_SEC
            cur_lines = cur_lines[1:]

            metric_offset = 0
            for line in cur_lines:
                if line.startswith(metric_name):
                    break
                metric_offset += 1
            cur_lines = cur_lines[metric_offset:]

            metric_line = cur_lines[0]
            metric_search = re.search(".*?(\\d+).*", metric_line)
            metric = int(metric_search.group(1))
            stats.append((time, metric))
            lines = lines[segment_length:]

    df = pd.DataFrame(stats, columns=["Time", metric_name])
    df.plot(x="Time", y=metric_name, kind="line", title=metric_name)
    plt.show()


def analyze_dstats(category_name: str, metric_name: str):
    stats = []
    # TODO UPDATE
    segment_length = 6
    with open(DSTAT_FILE_NAME, "r") as f:
        lines = f.readlines()
        while len(lines) > 0:
            cur_lines = lines[:segment_length]

            time_line = cur_lines[0]
            time_search = re.search("Time: (\\d+)", time_line)
            time = int(time_search.group(1)) / NS_PER_SEC
            cur_lines = cur_lines[1:]

            category_offset = 0
            category_line = cur_lines[0]
            categories = category_line.split(" ")
            for category in categories:
                if category_name in category:
                    break
                category_offset += 1
            cur_lines = cur_lines[1:]

            metric_offset = 0
            metric_name_line = cur_lines[0]
            metric_name_categories = metric_name_line.split("|")
            metric_names_all = metric_name_categories[category_offset]
            metric_names = metric_names_all.strip().split()
            for cur_metric_name in metric_names:
                if metric_name in cur_metric_name:
                    break
                metric_offset += 1
            cur_lines = cur_lines[1:]

            metric_line = cur_lines[0]
            metric_categories = metric_line.split("|")
            metric_category = metric_categories[category_offset]
            metrics = metric_category.strip().split()
            metric = metrics[metric_offset]

            stats.append((time, metric))
            lines = lines[segment_length:]

    clean_stats = []
    for time, metric in stats:
        clean_metric = metric
        if clean_metric.endswith("G"):
            clean_metric = float(clean_metric[:-1])
        elif clean_metric.endswith("M"):
            clean_metric = float(clean_metric[:-1]) * 1000
        else:
            clean_metric = float(clean_metric)
        clean_stats.append((time, clean_metric))

    df = pd.DataFrame(clean_stats, columns=["Time", f"{category_name} {metric_name}"])
    df.plot(x="Time", y=f"{category_name} {metric_name}", kind="line", title=f"{category_name} {metric_name}")
    plt.show()


def analyze_postgres_process_stats(file: str):
    df = pd.read_json(file)
    df[START_TIME] = df[START_TIME_NS] / NS_PER_SEC
    trim_columns = ["startup recovering", "walreceiver streaming"]
    for column in df.columns:
        new_column = " ".join(column.split()[1:])
        if any([trim_column in new_column for trim_column in trim_columns]):
            words = new_column.split()
            trim_word = words[-1]
            trim_words = trim_word.split("_")
            new_column_words = words[:-1] + trim_words[1:]
            new_column = " ".join(new_column_words)

        if column != START_TIME and column != START_TIME_NS:
            df = df.rename(columns={column: new_column})

    columns = [column for column in df.columns]
    columns.remove(START_TIME)
    columns.remove(START_TIME_NS)

    # df.plot(x=START_TIME, y=columns, kind="line", title=f"Postgres Process I/O")
    # plt.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))
    # plt.subplots_adjust(right=0.59)
    # plt.show()

    for column in columns:
        df.plot(x=START_TIME, y=column, kind="line", title=column)
        plt.show()


def analyze_benchbase_throughput():
    stats = []
    with open(THROUGHPUT_FILE_NAME, "r") as f:
        for line in f.readlines():
            if "Throughput" in line:
                time_search = re.search("\\[INFO ] (\\d+-\\d+-\\d+ \\d+:\\d+:\\d+,\\d+) \\[Thread", line)
                date_time_str = time_search.group(1)
                date_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S,%f")
                epoch = date_time.timestamp()

                throughput_search = re.search("Throughput: (\\d+.\\d+) txn/sec", line)
                throughput = float(throughput_search.group(1))
                stats.append((epoch, throughput))

    df = pd.DataFrame(stats, columns=["Time", "Throughput"])
    df.plot(x="Time", y="Throughput", kind="line", title=f"Throughput txn/sec")
    plt.show()


if __name__ == '__main__':
    main()
