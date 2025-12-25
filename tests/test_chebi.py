# TODO: Only runs in the moment with podman, not prepared for docker yet.
import logging
import shutil
import subprocess
import time
import zipfile
from pathlib import Path

import pytest
from click.testing import CliRunner
from neo4j import GraphDatabase, Result
from neo4j.exceptions import ServiceUnavailable
from sqlalchemy import Engine, create_engine

from biokb_chebi.cli import main
from biokb_chebi.constants import NEO4J_USER
from biokb_chebi.db import models
from biokb_chebi.db.manager import DbManager
from biokb_chebi.rdf.neo4j_importer import Neo4jImporter
from biokb_chebi.rdf.turtle import TurtleCreator

logger = logging.getLogger(__name__)

TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR / "data"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test_passwd"

engine: Engine = create_engine(
    f"sqlite:///",
)

container_engine = None
if shutil.which("podman"):
    container_engine = "podman"
elif shutil.which("docker"):
    container_engine = "docker"


def is_neo4j_responsive(
    uri="bolt://localhost:7687", user=NEO4J_USER, password=NEO4J_PASSWORD
) -> bool:
    try:
        with GraphDatabase.driver(uri, auth=(user, password)) as driver:
            driver.verify_connectivity()
        return True
    except Exception as e:
        logger.info(f"Wait for Neo4j to be responsive: {e}")
        return False


def start_neo4j_container():
    subprocess.run(f"{container_engine} rm -f neo4j-test".split(" "))
    command = f"{container_engine} run -d --name neo4j-test -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH={NEO4J_USER}/{NEO4J_PASSWORD} neo4j:5".split(
        " "
    )

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        container_id = result.stdout.strip()
        logger.info(
            f"Neo4j container started with ID: {container_id}. Waiting for it to be ready..."
        )
        # check if the database is ready
        for _ in range(30):
            try:
                if is_neo4j_responsive():
                    logger.info("Neo4j is responsive and ready to accept connections.")
                    break
            except ServiceUnavailable:
                pass
            time.sleep(1)
        return container_id
    else:
        logger.error("Error starting container:\n %s", result.stderr)
        return None


def remove_neo4j_container(container_id: str):
    command = ["podman", "rm", "-f", container_id]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        logger.info(f"Neo4j container {container_id} stopped and removed.")
    else:
        logger.error("Error stopping/removing container:\n %s", result.stderr)


@pytest.fixture
def dbm() -> DbManager:
    dbm = DbManager(engine)
    dbm._set_data_folder(str(DATA_DIR))
    return dbm


@pytest.fixture
def tc() -> TurtleCreator:
    tc = TurtleCreator(engine)
    tc._set_ttls_folder(str(DATA_DIR.joinpath("ttls")))
    return tc


class TestDataImport:
    """Test data import from ChEBI data files."""

    def test_import_data(self, dbm: DbManager) -> None:
        """Check if SQLite file exists if database is created."""
        dbm.import_data(keep_files=True)
        with dbm.Session() as session:
            assert session.query(models.ChemicalData).count() == 10
            assert session.query(models.Comment).count() == 3
            assert session.query(models.Compound).count() == 10
            assert session.query(models.DatabaseAccession).count() == 10
            assert session.query(models.Name).count() == 10
            assert session.query(models.Reference).count() == 10
            assert session.query(models.Relation).count() == 9
            assert session.query(models.RelationType).count() == 11
            assert session.query(models.Source).count() == 93
            assert session.query(models.Status).count() == 3
            assert session.query(models.Structure).count() == 10


class TestTurtleCreation:
    """Test Turtle creation from the database."""

    def test_create_turtle(self, dbm: DbManager, tc: TurtleCreator) -> None:
        """Check if Turtle file is created."""
        dbm.import_data(keep_files=True)
        path_to_zip_file = tc.create_ttls()
        path = Path(path_to_zip_file)

        assert path.exists()
        assert path.stat().st_size > 0
        # get list of files in the zip file

        expected_file_set = {
            "inchi.ttl",
            "name.ttl",
            "relation.ttl",
            "compound.ttl",
            "brenda_ligand_xref.ttl",
            "eccode_xref.ttl",
            "gxa_expt_xref.ttl",
        }
        with zipfile.ZipFile(path, "r") as zip_ref:
            assert set(zip_ref.namelist()) == expected_file_set

        # Clean up
        path.unlink()


class TestNeo4jImport:
    """Test Neo4j import from Turtle files."""

    def test_import_to_neo4j(
        self,
        dbm: DbManager,
        tc: TurtleCreator,
    ) -> None:
        """Check if data is imported into Neo4j."""
        if container_engine is None:
            pytest.skip("Neither podman nor docker is available.")

        container_id = start_neo4j_container()

        if container_id is None:
            pytest.skip("Could not start Neo4j container.")

        dbm.import_data(keep_files=True)
        path_to_zip_file = tc.create_ttls()

        importer = Neo4jImporter(
            neo4j_uri="bolt://localhost:7687",
            neo4j_user=NEO4J_USER,
            neo4j_pwd=NEO4J_PASSWORD,
        )
        importer._set_test_zipped_ttls_path(path_to_zip_file)
        importer.import_ttls()

        with importer.driver.session() as session:
            result: Result = session.run("MATCH (n:Compound) RETURN COUNT(n) AS count")
            record = result.single()
            assert record is not None
            count = record["count"]
            assert count == 10

            result = session.run("MATCH (n:OtherName) RETURN COUNT(n) AS count")
            record = result.single()
            assert record is not None
            count = record["count"]
            assert count == 9

            result = session.run("MATCH (n:InChI) RETURN COUNT(n) AS count")
            record = result.single()
            assert record is not None
            count = record["count"]
            assert count == 8

        # Clean up
        Path(path_to_zip_file).unlink()
        remove_neo4j_container(container_id)


class TestCLI:
    """Test CLI commands."""

    def test_cli_help(self) -> None:
        """Check if CLI help works."""
        runner = CliRunner()
        # Simuliert den Aufruf: biokb-chebi --help
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Options:" in result.output

    def test_cli_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output
