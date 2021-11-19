SIZE = "size"
COPY_TIME = "copy_time_ns"
DOCKER_START_UP_TIME = "docker_start_up_time"
RESET_WAL_TIME = "reset_wal_time"
POSTGRES_STARTUP_TIME = "postgres_startup_time"
TEARDOWN_TIME = "teardown_time"
VALID = "valid"

NS_PER_SEC = 1000000000

# TODO turn into command line arg
FILE_NAME = "results/final/zfs/scale_factors/128gb/test_result_1637260216.8914044.json_127G"


def main():
    # df = pd.read_json(FILE_NAME)
    #
    # df["copy_time"] = df[COPY_TIME] / NS_PER_SEC
    #
    # df.plot(x="global_iteration", y="copy_time", kind="line", title="Copy Time")
    # plt.show()
    startup_times = [1269269477615, 879762594502, 2181172736367, 9621497411011]
    startup_times = [startup_time / NS_PER_SEC for startup_time in startup_times]
    sum = 0
    for startup_time in startup_times:
        sum += startup_time
    avg = sum / len(startup_times)
    print(avg)


if __name__ == '__main__':
    main()
