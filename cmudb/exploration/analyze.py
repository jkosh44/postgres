import pandas as pd
from matplotlib import pyplot as plt

ITERATION = "iteration"
COPY_TIME_NS = "copy_time_ns"
COPY_TIME = "copy_time"
STARTUP_TIME_NS = "startup_time_ns"
STARTUP_TIME = "startup_time"
VALID = "valid"

NS_PER_SEC = 1000000000

# TODO turn into command line arg
FILE_NAME = "results/not_cow_tuned_12hr_checkpoint.json"


def main():
    df = pd.read_json(FILE_NAME)
    df[COPY_TIME] = df[COPY_TIME_NS] / NS_PER_SEC
    df[STARTUP_TIME] = df[STARTUP_TIME_NS] / NS_PER_SEC
    df.plot(x=ITERATION, y=[COPY_TIME, STARTUP_TIME], kind="line", title="COW with Checkpoints (seconds)")
    # plt.show()
    print(df[[STARTUP_TIME, COPY_TIME]].describe())


if __name__ == '__main__':
    main()
