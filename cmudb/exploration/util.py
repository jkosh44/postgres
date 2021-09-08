import subprocess
from typing import List
from typing import Union

import sys

# TODO make cmd line args maybe
PROJECT_ROOT = "../../"
ENV_FOLDER = "../env/"
CONTAINER_BIN_DIR = "/home/terrier/repo/build/bin/"
EXPLORATION_PORT = 42666
# This takes a couple of minutes to create. Just add more 0s to increase time
SERIES_LENGTH = 1000000000

PRIMARY = "primary"
REPLICA = "replica"


def execute_sys_command(cmd: Union[str, List[str]], block: bool = True,
                        forward_output: bool = True, cwd: str = None, env=None) -> subprocess.Popen:
    if isinstance(cmd, str):
        cmd = cmd.split(" ")
    res = subprocess.Popen(cmd, stdout=sys.stdout if forward_output else subprocess.DEVNULL,
                           stderr=sys.stderr if forward_output else subprocess.DEVNULL, cwd=cwd, env=env)
    if block:
        res.communicate()

    return res
