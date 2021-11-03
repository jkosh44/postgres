import re

import pandas as pd
from matplotlib import pyplot as plt

CHECKPOINT_TIME_NS = "checkpoint_time_ns"
CHECKPOINT_TIME = "checkpoint_time"
START_TIME_NS = "start_time_ns"
START_TIME = "start_time"
VALID = "valid"

NS_PER_SEC = 1000000000

TEST_FILE_NAME = "results/zfs/checkpoint/test_result_1635904882.374361.json"
IO_FILE_NAME = "results/zfs/checkpoint/iostats_1635904524.2487922"
SSD_FILE_NAME = "results/zfs/checkpoint/ssdstats_1635904882.374361"


def main():
    analyze_checkpoint_time()
    analyze_io_stats()
    analyze_ssd_stats()


def analyze_checkpoint_time():
    measurements = [
        (CHECKPOINT_TIME_NS, CHECKPOINT_TIME),
        (START_TIME_NS, START_TIME)
    ]

    df = pd.read_json(TEST_FILE_NAME)
    for ns_measurement, sec_measurement in measurements:
        df[sec_measurement] = df[ns_measurement] / NS_PER_SEC

    valid_measurements = df[df[VALID]]

    valid_measurements.plot(x=START_TIME, y=CHECKPOINT_TIME, kind="line", title="Checkpoint")
    plt.show()


def analyze_io_stats():
    stats = []
    metric_name = "wkB/s"
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


def analyze_ssd_stats():
    stats = []
    metric_name = "temperature"
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
            print(metric_line)
            metric_search = re.search(".*?(\\d+).*", metric_line)
            metric = int(metric_search.group(1))
            print(metric)
            stats.append((time, metric))
            lines = lines[segment_length:]

    df = pd.DataFrame(stats, columns=["Time", metric_name])
    df.plot(x="Time", y=metric_name, kind="line", title=metric_name)
    plt.show()


if __name__ == '__main__':
    main()
