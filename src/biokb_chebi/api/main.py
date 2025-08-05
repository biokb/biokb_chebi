import logging
import os
import secrets
from contextlib import asynccontextmanager
from typing import Annotated, Dict

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from biokb_chebi.api import schemas
from biokb_chebi.api.query_tools import build_dynamic_query
from biokb_chebi.api.tags import Tag
from biokb_chebi.db import manager, models

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

USERNAME = os.environ.get("API_USERNAME", "admin")
PASSWORD = os.environ.get("API_PASSWORD", "admin")


def get_session():
    with manager.DbManager().Session() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # dbm.drop_db()
    dbm = manager.DbManager()
    yield
    # Clean up
    pass


description = """A RESTful API for ChEBI."""

app = FastAPI(
    title="RESTful API for ChEBI",
    description=description,
    version="0.0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def verify_credentials(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    is_correct_username = secrets.compare_digest(credentials.username, USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


# tag: Database Management
# ========================

@app.get("/", tags=["Manage"])
def check_status() -> dict:
    return {"msg": "Running!"}


@app.post(path="/import_data/", response_model=dict[str, int], tags=[Tag.DBMANAGE])
def import_data(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
) -> dict[str, int]:
    """Load a tsv file in database."""
    dbm = manager.DbManager()
    return dbm.import_data()


# tag: Compound
# ========================


@app.get(
    "/compounds/", response_model=schemas.CompoundSearchResults, tags=[Tag.COMPOUND]
)
async def search_compounds(
    search: schemas.CompoundSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    """
    Search compounds.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Compound,
        db=session,
        limit=limit,
        offset=offset,
    )


# tag: Chemical Data
# ========================


@app.get(
    "/chemical_data/",
    response_model=schemas.ChemicalDataSearchResults,
    tags=[Tag.CHEMICAL_DATA],
)
async def search_chemical_data(
    search: schemas.ChemicalDataSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    """Search chemical_data.

    type(s) are:
        - CHARGE
        - FORMULA
        - MASS
        - MONOISOTOPIC MASS
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.ChemicalData,
        db=session,
        limit=limit,
        offset=offset,
    )


# tag: INCHI
# ========================


@app.get(
    "/inchi/",
    response_model=schemas.InchiSearchResults,
    tags=[Tag.INCHI],
)
async def search_inchi(
    search: schemas.InchiSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    """Search InChI."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Inchi,
        db=session,
        limit=limit,
        offset=offset,
    )


# tag: DatabaseAccession
# ========================


@app.get(
    "/database_accession/",
    response_model=schemas.DatabaseAccessionSearchResults,
    tags=[Tag.DATABASE_ACCESSION],
)
async def search_database_accession(
    search: schemas.DatabaseAccessionSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    """Search Database Accession."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.DatabaseAccession,
        db=session,
        limit=limit,
        offset=offset,
    )


# tag: Name
# ========================
@app.get(
    "/name/",
    response_model=schemas.NameSearchResults,
    tags=[Tag.NAME],
)
async def search_name(
    search: schemas.NameSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    """Search Name."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Name,
        db=session,
        limit=limit,
        offset=offset,
    )


# tag: Relation
# ========================


@app.get(
    "/relation/",
    response_model=schemas.RelationSearchResults,
    tags=[Tag.RELATION],
)
async def search_relation(
    search: schemas.RelationSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    """Search Relation."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Relation,
        db=session,
        limit=limit,
        offset=offset,
    )


# tag: Reference
# ========================
@app.get(
    "/reference/",
    response_model=schemas.ReferenceSearchResults,
    tags=[Tag.REFERENCE],
)
async def search_reference(
    search: schemas.ReferenceSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
):
    """Search Reference."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Reference,
        db=session,
        limit=limit,
        offset=offset,
    )
