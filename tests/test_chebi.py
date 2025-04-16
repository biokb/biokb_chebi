"""Test ChEBI import and export to ttl.

Make sure you have started the test podman-compose with 

`podman-compose -f docker-compose-test.yml up -d`
"""

import os
import os.path
import zipfile

from biokb_chebi.db import models as models
from biokb_chebi.db.importer import DatabaseImporter
from biokb_chebi.manager import MySQLDatabase
from biokb_chebi.neo4j_importer import Neo4jImporter
from biokb_chebi.rdf.turtle import TurtleCreator
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from .docker_compose_defaults import (
    MYSQL_DATABASE_TEST,
    MYSQL_HOST_TEST,
    MYSQL_PASSWORD_TEST,
    MYSQL_PORT_TEST,
    MYSQL_USER_TEST,
    NEO4J_PASSWD_TEST,
    NEO4J_URI_TEST,
    NEO4J_USER_TEST,
)

TEST_DATA_FOLDER = os.path.join("tests", "data")
TTLS_ZIP_PATH = os.path.join(TEST_DATA_FOLDER, "ttls.zip")


def get_engine() -> Engine:
    """Get SQLAlchemy engine.

    Returns:
        _type_: _description_
    """
    return create_engine(
        (
            f"mysql+pymysql://{MYSQL_USER_TEST}:{MYSQL_PASSWORD_TEST}@{MYSQL_HOST_TEST}:{MYSQL_PORT_TEST}/{MYSQL_DATABASE_TEST}"
        )
    )


class TestMySQLImporter:
    """MySQL importer test class."""

    table_count = {
        "chebi_compound": 105,
        "chebi_chemical_data": 50,
        "chebi_comment": 4,
        "chebi_database_accession": 105,
        "chebi_inchi": 105,
        "chebi_name": 67,
        "chebi_relation": 28,
        "chebi_reference": 60,
    }

    def setup_class(self):
        """Setup test class method."""
        self.engine = get_engine()
        self.config_db = MySQLDatabase(
            config_file=os.path.join(TEST_DATA_FOLDER, "config-tests.ini")
        )

    def test_import_db(self):
        """Test the import into the database."""
        importer = DatabaseImporter(engine=self.engine, data_folder=TEST_DATA_FOLDER)
        assert importer.import_db() == self.table_count

    def test_import_db_with_config(self):
        """Test the import into the database."""
        importer = DatabaseImporter(
            engine=self.config_db.engine, data_folder=TEST_DATA_FOLDER
        )
        assert importer.import_db() == self.table_count

    def test_number_of_entries(self):
        """Test the number of entries after import."""
        with Session(self.engine) as session:
            num_compound = session.query(models.Compound).count()
            assert num_compound == self.table_count["chebi_compound"]

            num_chemical_data = session.query(models.ChemicalData).count()
            assert num_chemical_data == self.table_count["chebi_chemical_data"]

            num_comment = session.query(models.Comment).count()
            assert num_comment == self.table_count["chebi_comment"]

            num_da = session.query(models.DatabaseAccession).count()
            assert num_da == self.table_count["chebi_database_accession"]

            num_inchi = session.query(models.Inchi).count()
            assert num_inchi == self.table_count["chebi_inchi"]

            num_name = session.query(models.Name).count()
            assert num_name == self.table_count["chebi_name"]

            num_rel = session.query(models.Relation).count()
            assert num_rel == self.table_count["chebi_relation"]

            num_ref = session.query(models.Reference).count()
            assert num_ref == self.table_count["chebi_reference"]


class TestTurtleCreator:
    """Turtle creator test class."""

    expected_file_list = {
        "cas.ttl",
        "compound.ttl",
        "inchi.ttl",
        "name.ttl",
        "patent.ttl",
        "relation.ttl",
    }

    def setup_class(self):
        """Setup test class method."""
        self.engine = get_engine()
        self.config_db = MySQLDatabase(
            config_file=os.path.join(TEST_DATA_FOLDER, "config-tests.ini")
        )

    def test_create_turtles(self):
        """Test create zipped file with turtle files."""

        if os.path.exists(TTLS_ZIP_PATH):
            os.remove(TTLS_ZIP_PATH)
        turtle_creator = TurtleCreator(
            engine=self.engine, export_to_folder=TEST_DATA_FOLDER
        )
        turtle_creator.create_all_ttls()

        assert os.path.exists(TTLS_ZIP_PATH) is True

        zip = zipfile.ZipFile(TTLS_ZIP_PATH)
        file_list = set(zip.namelist())

        assert self.expected_file_list == file_list

    def test_create_turtles_with_config(self):
        """Test create zipped file with turtle files."""

        if os.path.exists(TTLS_ZIP_PATH):
            os.remove(TTLS_ZIP_PATH)
        turtle_creator = TurtleCreator(
            engine=self.config_db.engine, export_to_folder=TEST_DATA_FOLDER
        )
        turtle_creator.create_all_ttls()

        assert os.path.exists(TTLS_ZIP_PATH) is True

        zip = zipfile.ZipFile(TTLS_ZIP_PATH)
        file_list = set(zip.namelist())

        assert self.expected_file_list == file_list


class TestNeo4jImporter:
    """Neo4j importer test class."""

    def test_import_ttls(self):
        """Test import of zipped file with ttls."""
        neo4j_importer = Neo4jImporter(
            neo4j_pwd=NEO4J_PASSWD_TEST,
            neo4j_user=NEO4J_USER_TEST,
            neo4j_uri=NEO4J_URI_TEST,
            delete_existing_graph=True,
            path_or_url=TTLS_ZIP_PATH,
        )
        assert neo4j_importer.import_ttls() is True

        # auth = (NEO4J_USER_TEST, NEO4J_PASSWD_TEST)
        # with GraphDatabase.driver(uri=NEO4J_URI_TEST, auth=auth) as driver:
        #     records, summary, keys = driver.execute_query(
        #         "match (n:Compound) return count(n) as num",
        #         database_="neo4j",
        #     )
        #     assert records[0].data() == {"num": 3}

        #     driver.close()
