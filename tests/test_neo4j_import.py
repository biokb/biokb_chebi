import pytest
from neo4j import GraphDatabase


@pytest.fixture(scope="session")
def neo4j_driver(neo4j_container):
    """Create Neo4j driver from container."""
    user = "neo4j"
    password = "neo4j_password"

    driver = GraphDatabase.driver(
        neo4j_container.get_connection_url(), auth=(user, password)
    )

    # Verify connection works before returning
    driver.verify_connectivity()

    yield driver
    driver.close()


@pytest.fixture(autouse=True)
def cleanup_db(neo4j_driver):
    """Clean up database before and after each test."""
    yield
    # Clean after test only (not before, to avoid initialization issues)
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")


def test_create_user(neo4j_driver):
    with neo4j_driver.session() as session:
        session.run("CREATE (u:User {name: 'Alice'})")
        result = session.run("MATCH (u:User {name: 'Alice'}) RETURN u.name AS name")
        assert result.single()["name"] == "Alice"
