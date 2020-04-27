# -*- coding: utf-8 -*-
"""Contains shared code like fixtures"""

import os
import subprocess
from time import sleep

import pytest

DOCKER_NAME = os.getenv("DOCKERNAME", "exasol_test_default")
DOCKER_PORT = 34778


@pytest.fixture(scope="session", name="dockerstart")
def setup_exasol_docker(request):
    """Start Exasol docker container and remove it after tests complete."""
    import re

    global DOCKER_PORT
    global DOCKER_NAME

    run_container = [
        "docker",
        "run",
        "--privileged",
        "-d",
        "--rm",
        "-p",
        "8888",
        "--name",
        DOCKER_NAME,
        "exasol/docker-db:latest",
    ]
    get_port = [
        "docker",
        "inspect",
        "-f",
        """{{(index (index .NetworkSettings.Ports "8888/tcp") 0).HostPort}}""",
        DOCKER_NAME,
    ]

    is_running = subprocess.call(
        ["docker", "inspect", "-f", "{{.State.Running}}", DOCKER_NAME]
    )
    log = ["docker", "logs", DOCKER_NAME, "--tail", "10"]

    if is_running == 1:  # Exit status 0 for success, 1 for error (not running)
        print(f"Waiting for container {DOCKER_NAME} to start... ")
        subprocess.run(run_container)
    while True:
        current_log = subprocess.check_output(log).decode("utf-8")
        result = re.search(".*Started.*exasql .*", current_log)
        if result:
            print("Container is up and running!")
            break
        sleep(10)

    DOCKER_PORT = subprocess.check_output(get_port, universal_newlines=True)
    print(DOCKER_PORT)
    print(f"Exasol container port: {DOCKER_PORT}")

    def tear_down_exasol_docker():
        """Stop Exasol Docker container."""
        stop_container = ["docker", "stop", DOCKER_NAME]
        print(f"Test execution completed, stopping {DOCKER_NAME} container")
        subprocess.run(stop_container)

    request.addfinalizer(tear_down_exasol_docker)


@pytest.fixture(scope="session")
def exaplus(dockerstart, request):
    """Helper to call exaplus"""

    def _exaplus(filename):

        cmd_response = subprocess.call(
            [
                "exaplus",
                "-c",
                "localhost:%s" % DOCKER_PORT,
                "-u",
                "sys",
                "-p",
                "exasol",
                "-f",
                filename,
            ]
        )

        return cmd_response

    return _exaplus


@pytest.fixture(scope="session")
def query(request):
    """Helper to query Exasol to connect to and query Exasol"""
    import pyexasol

    conn = pyexasol.connect(
        dsn="localhost:%s" % DOCKER_PORT, user="sys", password="exasol"
    )

    def _query(query_str):
        result = conn.export_to_pandas(query_str)
        print(result)
        return result

    return _query


@pytest.fixture(scope="session")
def set_up_schema():
    """"Helper for Scheme Setup"""
    bin_path = "1"
    return bin_path
