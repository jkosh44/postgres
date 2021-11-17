import pandas as pd
from matplotlib import pyplot as plt

SIZE = "size"
COPY_TIME = "copy_time_ns"
DOCKER_START_UP_TIME = "docker_start_up_time"
RESET_WAL_TIME = "reset_wal_time"
POSTGRES_STARTUP_TIME = "postgres_startup_time"
TEARDOWN_TIME = "teardown_time"
VALID = "valid"

NS_PER_SEC = 1000000000

# TODO turn into command line arg
FILE_NAME = "results/final/zfs/scale_factors/35g/test_result_1637110725.7930582.json_35G"


def main():
    df = pd.read_json(FILE_NAME)

    df["copy_time"] = df[COPY_TIME] / NS_PER_SEC

    df.plot(x="global_iteration", y="copy_time", kind="line", title="Copy Time")
    plt.show()


if __name__ == '__main__':
    main()
