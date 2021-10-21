from data_copy import destroy_exploratory_data_cow
from pgnp_docker import cleanup_docker_env


def main():
    cleanup_docker_env()
    destroy_exploratory_data_cow()


if __name__ == "__main__":
    main()
