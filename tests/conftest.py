import os
import subprocess
import time

import pytest
from testcontainers.neo4j import Neo4jContainer


@pytest.fixture(scope="session", autouse=True)
def setup_podman_environment():
    """
    Configures environment variables for Testcontainers
    when using Podman.
    """
    # 1. Check if DOCKER_HOST is already set, otherwise search for path
    if "DOCKER_HOST" not in os.environ:
        try:
            # Try to find the path of the current user socket of Podman
            result = subprocess.run(
                ["podman", "info", "--format", "{{.Host.RemoteSocket.Path}}"],
                capture_output=True,
                text=True,
                check=True,
            )
            socket_path = result.stdout.strip()
            if socket_path:
                # Verify socket exists, if not try to activate it
                if not os.path.exists(socket_path):
                    # Try to start the socket service
                    subprocess.run(
                        ["systemctl", "--user", "start", "podman.socket"],
                        capture_output=True,
                        timeout=5,
                    )
                os.environ["DOCKER_HOST"] = f"unix://{socket_path}"
        except Exception as e:
            # If Podman is not installed or an error occurs,
            # we leave it at default (Docker)
            print(f"Warning: Could not configure Podman: {e}")
            pass

    # 2. Disable Ryuk (often problematic under Podman due to permissions)
    # Ryuk is the "garbage collector" container of Testcontainers.
    os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"


@pytest.fixture(scope="session")
def neo4j_container():
    # Important: Fully qualified image name for Podman
    # Pass password directly to constructor (must be at least 8 characters)
    container = Neo4jContainer(
        "docker.io/library/neo4j:5.26.14", password="neo4j_password"
    )

    with container as neo4j:
        yield neo4j
