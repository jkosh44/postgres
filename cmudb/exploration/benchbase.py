import subprocess

from util import execute_sys_command, OutputStrategy

BENCHBASE_URL = "git@github.com:cmu-db/benchbase.git"
BENCHBASE_NAME = "benchbase-2021-SNAPSHOT"
BENCHBASE_TAR = f"./{BENCHBASE_NAME}.tgz"
BENCHBASE_DIR = f"./{BENCHBASE_NAME}"


def setup_benchbase():
    cleanup_benchbase()
    execute_sys_command(f"tar xvzf {BENCHBASE_TAR}")


# TODO consider pulling and building benchbase and being a little smarter
# TODO figure out how to do this without cwd (requires benchbase changes)
# TODO when benchbase abort output is fixed stop hiding output
def run_benchbase(create: bool, load: bool, execute: bool, block: bool = True,
                  output_strategy: OutputStrategy = OutputStrategy.Print) -> subprocess.Popen:
    benchbase_proc, _, _ = execute_sys_command(
        f"java -jar benchbase.jar -b ycsb -c ../postgres_ycsb_update_only_config.xml --create={create} --load={load}"
        f" --execute={execute}", cwd=BENCHBASE_DIR, block=block, output_strategy=output_strategy)
    return benchbase_proc


def cleanup_benchbase():
    execute_sys_command(f"rm -rf {BENCHBASE_DIR}")
