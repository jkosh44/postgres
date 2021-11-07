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

TEST_FILE_NAME = "results/zfs/checkpoint/increase_timeout/test_result_1636240563.7423668.json_42G"
IO_FILE_NAME = "results/zfs/checkpoint/increase_timeout/iostats_1636240563.7423668"
SSD_FILE_NAME = "results/zfs/checkpoint/increase_timeout/ssdstats_1636240563.7423668"


def main():
    analyze_postgres_stats_time(CHECKPOINT_TIME_NS, CHECKPOINT_TIME)
    analyze_postgres_stats(PRECHECKPOINT_DIRTY_PAGE)
    analyze_postgres_stats(POSTCHECKPOINT_DIRTY_PAGE)
    analyze_io_stats("wkB/s")
    analyze_io_stats("rkB/s")
    analyze_io_stats("r_await")
    analyze_io_stats("w_await")
    analyze_io_stats("%util")
    analyze_ssd_stats("temperature")


def analyze_postgres_stats_time(metric_name_ns: str, metric_name_sec: str):
    measurements = [
        (metric_name_ns, metric_name_sec),
        (START_TIME_NS, START_TIME)
    ]

    df = pd.read_json(TEST_FILE_NAME)
    for ns_measurement, sec_measurement in measurements:
        df[sec_measurement] = df[ns_measurement] / NS_PER_SEC

    valid_measurements = df[df[VALID]]

    valid_measurements.plot(x=START_TIME, y=metric_name_sec, kind="line", title=f"{metric_name_sec} (sec)")
    plt.show()


def analyze_postgres_stats(metric_name: str):
    df = pd.read_json(TEST_FILE_NAME)
    df[START_TIME] = df[START_TIME_NS] / NS_PER_SEC

    valid_measurements = df[df[VALID]]

    valid_measurements.plot(x=START_TIME, y=metric_name, kind="line", title=f"{metric_name}")
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


if __name__ == '__main__':
    main()
