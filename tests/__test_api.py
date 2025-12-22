"""Unlike test_chebi.py, these tests also work without a started container (Docker/Podman)

Just make sure to create a .venv, install all necessary libraries (`pip install -e .`) and install pytest (`pip install pytest`)
"""

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from biokb_chebi.api.main import app, get_session
from biokb_chebi.db.manager import DbManager

# Create a new test database engine (SQLite in-memory for testing)
os.makedirs("tests/dbs", exist_ok=True)
test_engine = create_engine("sqlite:///tests/dbs/test.db")
# test_engine = create_engine(
#     "mysql+pymysql://biokb_user:biokb_passwd@127.0.0.1:3307/biokb"
# )
TestSessionLocal = sessionmaker(bind=test_engine)

### NOTE: If you want to test the API yourself in your browser, remember to export the connection string first (`export CONNECTION_STR="sqlite:///tests/dbs/test.db"` in a Python terminal)


# Dependency override to use test database
def override_get_db() -> Generator[Session, None, None]:
    db: Session = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply the override to the FastAPI dependency
app.dependency_overrides[get_session] = override_get_db


@pytest.fixture()
def client_with_data() -> TestClient:
    # Create tables in the test database
    test_data_folder = os.path.join("tests", "dummy_data")
    dm = DbManager(test_engine, test_data_folder)
    dm.import_data()
    return TestClient(app)


def test_server(client_with_data: TestClient) -> None:
    response = client_with_data.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Running!"}


class TestCompound:
    def test_get_compound(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("compounds/?id=1")
        assert response.status_code == 200
        data = response.json()
        expected = {
            "count": 1,
            "offset": 0,
            "limit": 10,
            "results": [
                {
                    "id": 1,
                    "name": "N(alpha)-methyl-L-tryptophan",
                    "source": "ChEBI",
                    "chebi_accession": "CHEBI:1",
                    "status": "C",
                    "definition": "A N-methyl-L-alpha-amino acid  that is the N(alpha)-methyl derivative of L-tryptophan.",
                    "star": 3,
                    "modified_on": "2019-11-21",
                    "created_by": "ops$mennis",
                    "parent_id": None,
                    "chemicalData": [
                        {
                            "chemical_data": "0",
                            "source": "ChEMBL",
                            "type": "CHARGE",
                            "compound_id": 1,
                        }
                    ],
                    "comments": [
                        {
                            "text": "comment 1",
                            "created_on": "2004-12-09",
                            "datatype": "ChemicalData",
                            "datatype_id": 4448,
                            "compound_id": 1,
                        }
                    ],
                    "database_accessions": [
                        {
                            "accession_number": "IND85072840",
                            "type": "Agricola citation",
                            "source": "Europe PMC",
                            "compound_id": 1,
                        }
                    ],
                    "names": [
                        {
                            "name": "name 1",
                            "type": "BRAND NAME",
                            "source": "ChEBI",
                            "adapted": "F",
                            "language": "en",
                            "compound_id": 1,
                        }
                    ],
                    "references": [
                        {
                            "reference_id": "67-71-0",
                            "reference_db_name": "ACToR",
                            "location_in_ref": None,
                            "reference_name": None,
                            "compound_id": 1,
                        }
                    ],
                    "structures": [],
                    "inchis": [{"inchi": "InChI=1", "compound_id": 1}],
                }
            ],
        }
        assert data == expected

    def test_list_compounds(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/compounds/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3

    def test_list_compounds_offset(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/compounds/?offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1

    def test_list_compounds_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/compounds/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_compounds_offset_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("compounds/?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        expected = {
            "count": 3,
            "offset": 2,
            "limit": 2,
            "results": [
                {
                    "id": 3,
                    "name": "nalidixic acid",
                    "source": "ChEMBL",
                    "chebi_accession": "CHEBI:3",
                    "status": "C",
                    "definition": "A monocarboxylic acid comprising 1,8-naphthyridin-4-one substituted by carboxylic acid, ethyl and methyl groups at positions 3, 1, and 7, respectively. An orally administered antibacterial, it is used in the treatment of lower urinary-tract infections due to Gram-negative bacteria, including the majority of E. coli, Enterobacter, Klebsiella, and Proteus species.",
                    "star": 3,
                    "modified_on": "2017-06-19",
                    "created_by": "LOADER",
                    "parent_id": None,
                    "chemicalData": [
                        {
                            "chemical_data": "0",
                            "source": "KEGG DRUG",
                            "type": "CHARGE",
                            "compound_id": 3,
                        }
                    ],
                    "comments": [
                        {
                            "text": "comment 3",
                            "created_on": "2006-09-01",
                            "datatype": "DatabaseAccession",
                            "datatype_id": 99024,
                            "compound_id": 3,
                        }
                    ],
                    "database_accessions": [
                        {
                            "accession_number": "3196616",
                            "type": "Beilstein Registry Number",
                            "source": "Beilstein",
                            "compound_id": 3,
                        }
                    ],
                    "names": [
                        {
                            "name": "name 3",
                            "type": "BRAND NAME",
                            "source": "DrugBank",
                            "adapted": "F",
                            "language": "en",
                            "compound_id": 3,
                        }
                    ],
                    "references": [
                        {
                            "reference_id": "50026473",
                            "reference_db_name": "BindingDB",
                            "location_in_ref": None,
                            "reference_name": None,
                            "compound_id": 3,
                        }
                    ],
                    "structures": [],
                    "inchis": [{"inchi": "InChI=3", "compound_id": 3}],
                }
            ],
        }
        assert data == expected


class TestChemicalData:
    def test_get_chemical_data(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/chemical_data/?compound_id=1")
        assert response.status_code == 200
        data = response.json()
        expected = {
            "count": 1,
            "offset": 0,
            "limit": 10,
            "results": [
                {
                    "chemical_data": "0",
                    "source": "ChEMBL",
                    "type": "CHARGE",
                    "compound_id": 1,
                    "compound": {
                        "id": 1,
                        "name": "N(alpha)-methyl-L-tryptophan",
                        "source": "ChEBI",
                        "chebi_accession": "CHEBI:1",
                        "status": "C",
                        "definition": "A N-methyl-L-alpha-amino acid  that is the N(alpha)-methyl derivative of L-tryptophan.",
                        "star": 3,
                        "modified_on": "2019-11-21",
                        "created_by": "ops$mennis",
                        "parent_id": None,
                    },
                }
            ],
        }
        assert data == expected

    def test_list_chemical_data(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/chemical_data/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3

    def test_list_chemical_data_offset(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/chemical_data/?offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_chemical_data_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/chemical_data/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_chemical_data_offset_limit(
        self, client_with_data: TestClient
    ) -> None:
        response = client_with_data.get("/chemical_data/?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1


class TestInChI:
    def test_get_inchi(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/inchi/?inchi=InChI%3D1")
        assert response.status_code == 200
        data = response.json()
        expected = {
            "count": 1,
            "offset": 0,
            "limit": 10,
            "results": [
                {
                    "inchi": "InChI=1",
                    "compound_id": 1,
                    "compound": {
                        "id": 1,
                        "name": "N(alpha)-methyl-L-tryptophan",
                        "source": "ChEBI",
                        "chebi_accession": "CHEBI:1",
                        "status": "C",
                        "definition": "A N-methyl-L-alpha-amino acid  that is the N(alpha)-methyl derivative of L-tryptophan.",
                        "star": 3,
                        "modified_on": "2019-11-21",
                        "created_by": "ops$mennis",
                        "parent_id": None,
                    },
                }
            ],
        }
        assert data == expected

    def test_list_inchi(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/inchi/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3

    def test_list_inchi_offset(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/inchi/?offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_inchi_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/inchi/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_inchi_offset_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/inchi/?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1


class TestDatabaseAccession:
    def test_get_database_accession(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/database_accession/?accession_number=257458")
        assert response.status_code == 200
        data = response.json()
        expected = {
            "count": 1,
            "offset": 0,
            "limit": 10,
            "results": [
                {
                    "accession_number": "257458",
                    "type": "Beilstein Registry Number",
                    "source": "Alan Wood's Pesticides",
                    "compound_id": 2,
                    "compound": {
                        "id": 2,
                        "name": "acetylhistone",
                        "source": "ChEBI",
                        "chebi_accession": "CHEBI:2",
                        "status": "E",
                        "definition": None,
                        "star": 1,
                        "modified_on": "2018-12-15",
                        "created_by": "ops$mennis",
                        "parent_id": None,
                    },
                }
            ],
        }
        assert data == expected

    def test_list_database_accession(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/database_accession/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3

    def test_list_database_accession_offset(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/database_accession/?offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_database_accession_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/database_accession/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_database_accession_offset_limit(
        self, client_with_data: TestClient
    ) -> None:
        response = client_with_data.get("/database_accession/?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1


class TestName:
    def test_get_name(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/name/?name=name%201")
        assert response.status_code == 200
        data = response.json()
        expected = {
            "count": 1,
            "offset": 0,
            "limit": 10,
            "results": [
                {
                    "name": "name 1",
                    "type": "BRAND NAME",
                    "source": "ChEBI",
                    "adapted": "F",
                    "language": "en",
                    "compound_id": 1,
                    "compound": {
                        "id": 1,
                        "name": "N(alpha)-methyl-L-tryptophan",
                        "source": "ChEBI",
                        "chebi_accession": "CHEBI:1",
                        "status": "C",
                        "definition": "A N-methyl-L-alpha-amino acid  that is the N(alpha)-methyl derivative of L-tryptophan.",
                        "star": 3,
                        "modified_on": "2019-11-21",
                        "created_by": "ops$mennis",
                        "parent_id": None,
                    },
                }
            ],
        }
        assert data == expected

    def test_list_name(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/name/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3

    def test_list_name_offset(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/name/?offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_name_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/name/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_name_offset_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/name/?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1


class TestRelation:
    def test_get_relation(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/relation/?final_id=2&init_id=1")
        assert response.status_code == 200
        data = response.json()
        expected = {
            "count": 1,
            "offset": 0,
            "limit": 10,
            "results": [
                {
                    "type": "has_functional_parent",
                    "status": "C",
                    "final_id": 2,
                    "init_id": 1,
                    "final_id_compound": {
                        "id": 2,
                        "name": "acetylhistone",
                        "source": "ChEBI",
                        "chebi_accession": "CHEBI:2",
                        "status": "E",
                        "definition": None,
                        "star": 1,
                        "modified_on": "2018-12-15",
                        "created_by": "ops$mennis",
                        "parent_id": None,
                    },
                    "init_id_compound": {
                        "id": 1,
                        "name": "N(alpha)-methyl-L-tryptophan",
                        "source": "ChEBI",
                        "chebi_accession": "CHEBI:1",
                        "status": "C",
                        "definition": "A N-methyl-L-alpha-amino acid  that is the N(alpha)-methyl derivative of L-tryptophan.",
                        "star": 3,
                        "modified_on": "2019-11-21",
                        "created_by": "ops$mennis",
                        "parent_id": None,
                    },
                }
            ],
        }
        assert data == expected

    def test_list_relation(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/relation/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3

    def test_list_relation_offset(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/relation/?offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_relation_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/relation/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_relation_offset_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/relation/?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1


class TestReference:
    def test_get_reference(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/reference/?reference_id=50026473")
        assert response.status_code == 200
        data = response.json()
        expected = {
            "count": 1,
            "offset": 0,
            "limit": 10,
            "results": [
                {
                    "reference_id": "50026473",
                    "reference_db_name": "BindingDB",
                    "location_in_ref": None,
                    "reference_name": None,
                    "compound_id": 3,
                    "compound": {
                        "id": 3,
                        "name": "nalidixic acid",
                        "source": "ChEMBL",
                        "chebi_accession": "CHEBI:3",
                        "status": "C",
                        "definition": "A monocarboxylic acid comprising 1,8-naphthyridin-4-one substituted by carboxylic acid, ethyl and methyl groups at positions 3, 1, and 7, respectively. An orally administered antibacterial, it is used in the treatment of lower urinary-tract infections due to Gram-negative bacteria, including the majority of E. coli, Enterobacter, Klebsiella, and Proteus species.",
                        "star": 3,
                        "modified_on": "2017-06-19",
                        "created_by": "LOADER",
                        "parent_id": None,
                    },
                }
            ],
        }
        assert data == expected

    def test_list_reference(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/reference/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3

    def test_list_reference_offset(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/reference/?offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_reference_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/reference/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_list_reference_offset_limit(self, client_with_data: TestClient) -> None:
        response = client_with_data.get("/reference/?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
