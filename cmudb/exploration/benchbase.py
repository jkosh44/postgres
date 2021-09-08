from util import execute_sys_command

BENCHBASE_URL = "git@github.com:cmu-db/benchbase.git"
BENCHBASE_NAME = "benchbase-2021-SNAPSHOT"
BENCHBASE_TAR = f"./{BENCHBASE_NAME}.tgz"
BENCHBASE_DIR = f"./{BENCHBASE_NAME}"


def setup_benchbase():
    cleanup_benchbase()
    execute_sys_command(f"tar xvzf {BENCHBASE_TAR}")


# TODO consider pulling and building benchbase and being a little smarter
# TODO figure out how to do this without going to that random directory
def run_benchbase(create: bool = True, load: bool = True, execute: bool = True):
    return execute_sys_command(
        f"java -jar benchbase.jar -b tpcc -c ../postgres_tpcc_config.xml --create={create} --load={load}"
        f" --execute={execute}", cwd=BENCHBASE_DIR)


def cleanup_benchbase():
    execute_sys_command(f"rm -rf {BENCHBASE_DIR}")
