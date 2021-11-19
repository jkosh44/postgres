import pandas as pd
from matplotlib import pyplot as plt

RAW_TIME = "time"
REPLICA_LAG = "replica_lag"
CLEAN_TIME = "clean_time"

NS_PER_SEC = 1000000000

# TODO turn into command line arg
LAG_FILE_NAME = "results/final/zfs/replay_lag/replica_lag_1637282788.335872.json"
EXPLORATORY_FILE_NAME = "results/final/zfs/replay_lag/exploratory_time_1637282788.335872"


def main():
    df = pd.read_json(LAG_FILE_NAME)

    start_time = df[RAW_TIME][0]
    print(start_time)

    with open(EXPLORATORY_FILE_NAME, "r") as f:
        exploratory_startup = (int(f.readline()) - start_time) / NS_PER_SEC

    print(exploratory_startup)

    df[CLEAN_TIME] = (df[RAW_TIME] - start_time) / NS_PER_SEC

    df = df[df[CLEAN_TIME] < 2692]

    df.plot(x=CLEAN_TIME, y=REPLICA_LAG, kind="line", title="Replay lag", legend=None, xlabel="Time (sec)",
            ylabel="Lag (sec)")
    plt.axvline(x=exploratory_startup)
    plt.show()


if __name__ == '__main__':
    main()
