import pandas as pd
from matplotlib import pyplot as plt

SIZE = "size"
COPY_TIME = "copy_time"
DOCKER_START_UP_TIME = "docker_start_up_time"
RESET_WAL_TIME = "reset_wal_time"
POSTGRES_STARTUP_TIME = "postgres_startup_time"
TEARDOWN_TIME = "teardown_time"
VALID = "valid"

NS_PER_SEC = 1000000000

# TODO turn into command line arg
FILE_NAME = "results/final/ext4/scale_factors/agg.json"


def main():
    # measurements = [COPY_TIME, RESET_WAL_TIME, POSTGRES_STARTUP_TIME]
    measurements = [COPY_TIME]
    # measurements = [RESET_WAL_TIME, POSTGRES_STARTUP_TIME]

    df = pd.read_json(FILE_NAME)

    df.plot(x=SIZE, y=measurements, kind="line", title="ZFS Copies", xlabel="Size (GB)", ylabel="Time (sec)",
            legend=None)
    # df.plot(x=SIZE, y=measurements, kind="line", title="Trimmed WAL", xlabel="Size (GB)", ylabel="Time (sec)")
    plt.show()


if __name__ == '__main__':
    main()
