import pandas as pd
from matplotlib import pyplot as plt

SIZE = "size"
CHECKPOINT = "checkpoint"
COPY = "copy"
DOCKER_STARTUP = "docker startup"
RESET_WAL = "reset_wal"
POSTGRES_STARTUP = "postgres startup"
TEARDOWN = "teardown"
PERCENT_VALID = "percent valid"

# TODO turn into command line arg
FILE_NAME = "results/zfs/final/agg.json"


def main():
    y = [
        CHECKPOINT,
        COPY,
        DOCKER_STARTUP,
        RESET_WAL,
        POSTGRES_STARTUP,
        TEARDOWN,
        PERCENT_VALID
    ]
    x = SIZE

    df = pd.read_json(FILE_NAME)
    for measure in y:
        df.plot(x=x, y=measure, kind="line", title=f"{measure} (seconds)")
        plt.show()


if __name__ == '__main__':
    main()
