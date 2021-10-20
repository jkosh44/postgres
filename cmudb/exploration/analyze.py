import pandas as pd
from matplotlib import pyplot as plt

ITERATION = "iteration"
CHECKPOINT_TIME_NS = "checkpoint_time_ns"
CHECKPOINT_TIME = "checkpoint_time"
COPY_TIME_NS = "copy_time_ns"
COPY_TIME = "copy_time"
DOCKER_STARTUP_TIME_NS = "docker_startup_time_ns"
DOCKER_STARTUP_TIME = "docker_startup_time"
RESET_WAL_TIME_NS = "reset_wal_time_ns"
RESET_WAL_TIME = "reset_wal_time"
POSTGRES_STARTUP_TIME_NS = "postgres_startup_time_ns"
POSTGRES_STARTUP_TIME = "postgres_startup_time"
TEARDOWN_TIME_NS = "teardown_time_ns"
TEARDOWN_TIME = "teardown_time"
TOTAL_TIME = "total_time"
VALID = "valid"

NS_PER_SEC = 1000000000

# TODO turn into command line arg
FILE_NAME = "results/zfs/cow_tuned_12hr_checkpoint_multidisk_reset.json"


def main():
    measurements = [
        (CHECKPOINT_TIME_NS, CHECKPOINT_TIME),
        (COPY_TIME_NS, COPY_TIME),
        (DOCKER_STARTUP_TIME_NS, DOCKER_STARTUP_TIME),
        (RESET_WAL_TIME_NS, RESET_WAL_TIME),
        (POSTGRES_STARTUP_TIME_NS, POSTGRES_STARTUP_TIME),
        (TEARDOWN_TIME_NS, TEARDOWN_TIME)
    ]
    sec_measurements = [sec_measurement for _, sec_measurement in measurements]

    df = pd.read_json(FILE_NAME)
    df[TOTAL_TIME] = 0
    for ns_measurement, sec_measurement in measurements:
        df[sec_measurement] = df[ns_measurement] / NS_PER_SEC
        df[TOTAL_TIME] += df[sec_measurement]

    valid_measurements = df[df[VALID]]
    # valid_measurements.plot(x=ITERATION, y=sec_measurements,
    #                         kind="line", title="COW (seconds)")
    valid_measurements.plot(x=ITERATION, y=sec_measurements, kind="bar",
                            stacked=True, title="COW (seconds)")
    plt.show()

    for sec_measurement in sec_measurements:
        print(valid_measurements[sec_measurement].describe())
    print(valid_measurements[TOTAL_TIME].describe())
    print(f"Percent Valid: {len(valid_measurements) / len(df)}")


if __name__ == '__main__':
    main()
