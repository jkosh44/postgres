import signal
import subprocess
import sys
from enum import Enum
from typing import List, Tuple, AnyStr
from typing import Union

# TODO make cmd line args maybe
PROJECT_ROOT = "../.."
ENV_FOLDER = "../env"
CONTAINER_BIN_DIR = "/home/terrier/repo/build/bin"
PGDATA_LOC = "/pgdata"
PGDATA_REPLICA_LOC = "/replica-pgdata"
PGDATA2_LOC = "/pgdata2"
PRIMARY_PORT = 15721
EXPLORATION_PORT = 42666
# This takes a couple of minutes to create. Just add more 0s to increase time
SERIES_LENGTH = 1000000000

PRIMARY = "primary"
REPLICA = "replica"
EXPLORATION = "exploration"

UTF_8 = "utf-8"


class OutputStrategy(Enum):
    Capture = (subprocess.PIPE, subprocess.PIPE)
    Print = (sys.stdout, sys.stderr)
    Hide = (subprocess.DEVNULL, subprocess.DEVNULL)


def execute_sys_command(cmd: Union[str, List[str]],
                        block: bool = True,
                        output_strategy: OutputStrategy = OutputStrategy.Print,
                        cwd: str = None,
                        env=None) -> Tuple[subprocess.Popen, AnyStr, AnyStr]:
    if isinstance(cmd, str):
        cmd = cmd.split(" ")

    res = subprocess.Popen(cmd, stdout=output_strategy.value[0], stderr=output_strategy.value[1], cwd=cwd, env=env)
    out = ""
    err = ""
    if block:
        out, err = res.communicate()
        out = out.decode(UTF_8) if out is not None else ""
        err = err.decode(UTF_8) if err is not None else ""

    return res, out., err


def stop_process(proc: subprocess.Popen, block: bool = True):
    proc.send_signal(signal.SIGINT)
    if block:
        try:
            proc.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            proc.terminate()
