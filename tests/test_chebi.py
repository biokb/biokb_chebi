import os
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine

from biokb_chebi.db import models
from biokb_chebi.db.manager import DbManager
from biokb_chebi.rdf.turtle import TurtleCreator

TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR / "data"

engine: Engine = create_engine(
    f"sqlite:///",
)


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
        # get list of files in the zip
        import zipfile

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
