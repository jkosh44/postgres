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
    measurements = [
        (CHECKPOINT_TIME_NS, CHECKPOINT_TIME),
        (START_TIME_NS, START_TIME)
    ]
    sec_measurements = [sec_measurement for _, sec_measurement in measurements]

    df = pd.read_json(TEST_FILE_NAME)
    for ns_measurement, sec_measurement in measurements:
        df[sec_measurement] = df[ns_measurement] / NS_PER_SEC

    valid_measurements = df[df[VALID]]

    print(valid_measurements)

    valid_measurements.plot(x=START_TIME, y=CHECKPOINT_TIME, kind="line",
                                 stacked=True, title="Checkpoint")
    plt.show()


if __name__ == '__main__':
    main()
