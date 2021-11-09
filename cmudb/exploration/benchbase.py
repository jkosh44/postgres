import re
import subprocess

from util import execute_sys_command, OutputStrategy

BENCHBASE_URL = "git@github.com:cmu-db/benchbase.git"
BENCHBASE_NAME = "benchbase-2021-SNAPSHOT"
BENCHBASE_TAR = f"./{BENCHBASE_NAME}.tgz"
BENCHBASE_DIR = f"./benchbase/{BENCHBASE_NAME}"


def setup_benchbase():
    cleanup_benchbase()
    execute_sys_command(f"tar xvzf {BENCHBASE_TAR}", cwd="./benchbase/")


# TODO consider pulling and building benchbase and being a little smarter
# TODO figure out how to do this without cwd (requires benchbase changes)
# TODO when benchbase abort output is fixed stop hiding output
# TODO paramterize inputs (config, benchmark)
def run_benchbase(create: bool, load: bool, execute: bool, block: bool = True,
                  output_strategy: OutputStrategy = OutputStrategy.Print) -> subprocess.Popen:
    benchbase_proc, _, _ = execute_sys_command(
        f"java -jar benchbase.jar -b ycsb -c ../noisepage_ycsb_update_only_config.xml --interval-monitor 60000 "
        f"--create={create} --load={load} --execute={execute}", cwd=BENCHBASE_DIR, block=block,
        output_strategy=output_strategy)

    return benchbase_proc


def cleanup_benchbase():
    execute_sys_command(f"rm -rf {BENCHBASE_DIR}")


def get_benchbase_throughput(benchbase_proc: subprocess.Popen):
    try:
        out, _ = benchbase_proc.communicate()
        out = out.decode("UTF-8")

        print(out)

        p = re.compile(
            "Rate limited reqs/s: Results\\(nanoSeconds=\\d+, measuredRequests=\\d+\\) = (\\d+.\\d+ requests/sec)")
        throughput = p.search(out)
        return throughput.group(1)
    except Exception as e:
        return f"Error getting throughput: {e}"
