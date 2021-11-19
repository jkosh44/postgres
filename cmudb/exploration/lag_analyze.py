import pandas as pd
from matplotlib import pyplot as plt

TIME = "time"
REPLICA_LAG = "replica_lag"

NS_PER_SEC = 1000000000

# TODO turn into command line arg
LAG_FILE_NAME = "results/final/zfs/replay_lag/replica_lag_1637282788.335872.json"
EXPLORATORY_FILE_NAME = "results/final/zfs/replay_lag/exploratory_time_1637282788.335872"


def main():
    exploratory_startup = 0
    with open(EXPLORATORY_FILE_NAME, "")
    df = pd.read_json(LAG_FILE_NAME)

    df.plot(x=TIME, y=REPLICA_LAG, kind="line", title="Replay lag")
    plt.show()


if __name__ == '__main__':
    main()
