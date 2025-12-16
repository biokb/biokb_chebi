"""Unlike test_chebi.py, these tests also work without a started container (Docker/Podman)

Just make sure to create a .venv, install all necessary libraries (`pip install -e .`) and install pytest (`pip install pytest`)
"""

import os

import pytest
from sqlalchemy import Engine, create_engine

from biokb_chebi.db import models
from biokb_chebi.db.manager import DbManager

sqlite_file_path = "./tests/dbs/test.db"
if os.path.exists(sqlite_file_path):
    os.remove(sqlite_file_path)
engine: Engine = create_engine(
    f"sqlite:///{sqlite_file_path}",
)


@pytest.fixture
def dbm():
    # Create tables in the test database
    test_data_folder = os.path.join("tests", "dummy_data")
    dbm = DbManager(engine, test_data_folder)
    return dbm


def test_engine_exists(dbm: DbManager):
    """Check if SQLAlchemy engine exists."""
    assert isinstance(dbm.__engine, Engine)


def test_import_data(dbm: DbManager):
    """Check if SQLite file exists if database is created."""
    dbm.import_data()
    with dbm.Session() as session:
        assert session.query(models.Compound).count() == 3
        assert session.query(models.ChemicalData).count() == 3
        assert session.query(models.Comment).count() == 3
        assert session.query(models.Inchi).count() == 3
        assert session.query(models.DatabaseAccession).count() == 3
        assert session.query(models.Name).count() == 3
        assert session.query(models.Relation).count() == 3
        assert session.query(models.Reference).count() == 3
        # NOTE: In the dummy data, Structure is empty since it is a complex database/table that would be too large and complicated
        # assert session.query(models.Structure).count() == 0
