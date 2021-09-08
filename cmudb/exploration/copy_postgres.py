import os

from benchbase import setup_benchbase, cleanup_benchbase
from pgnp_docker import start_docker, shutdown_docker
from util import execute_sys_command


def raw_copy():
    pass


def execute_sql(query: str):
    # TODO this is only primary
    env = os.environ.copy()
    env["PGPASSWORD"] = "terrier"
    cmd = "psql -h localhost -p 15721 -U noisepage -t -P pager=off".split(" ")
    cmd.append(f'--command={query}')
    cmd.append("noisepage")
    execute_sys_command(cmd, env=env)


def main():
    print("Starting Docker containers")
    docker_process = start_docker()
    print("Docker containers started successfully")

    # Load some data into primary for validation
    execute_sql("CREATE TABLE foo(a int);")
    execute_sql("INSERT INTO foo VALUES (42), (666);")
    execute_sql("SELECT * FROM foo;")

    print("Loading data")
    setup_benchbase()
    # TODO uncomment me
    # run_benchbase(create=True, load=True, execute=False)
    print("Data loaded")

    cleanup_benchbase()
    print("Killing Docker containers")
    shutdown_docker(docker_process)
    print("Docker containers killed successfully")

    # docker_thread.join()
    # Wait for DB to be up
    # Load data
    # Repeat
    #       Copy pgdata on replica
    #       Start primary server
    #       Validate that it was successful
    #       Delete copy


if __name__ == "__main__":
    main()
