import logging
import os
import secrets
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, Generator

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from biokb_chebi.api import schemas
from biokb_chebi.api.query_tools import SASearchResults, build_dynamic_query
from biokb_chebi.api.tags import Tag
from biokb_chebi.constants import (
    DB_DEFAULT_CONNECTION_STR,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USER,
    ZIPPED_TTLS_PATH,
)
from biokb_chebi.db import manager, models
from biokb_chebi.rdf.neo4j_importer import Neo4jImporter
from biokb_chebi.rdf.turtle import TurtleCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger: logging.Logger = logging.getLogger(__name__)

USERNAME: str = os.environ.get("API_USERNAME", "admin")
PASSWORD: str = os.environ.get("API_PASSWORD", "admin")


def get_engine() -> Engine:
    conn_url = os.environ.get("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
    engine: Engine = create_engine(conn_url)
    return engine


def get_session() -> Generator[Session, None, None]:
    engine: Engine = get_engine()
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize app resources on startup and cleanup on shutdown."""
    engine = get_engine()
    manager.DbManager(engine)
    yield
    # Clean up resources if needed
    pass


description = (
    "A RESTful API for BioKB-ChEBI. This is not an official ChEBI API."
    " Please refer to [EBI for official ChEBI services](https://www.ebi.ac.uk/chebi/)"
)

app = FastAPI(
    title="RESTful API for BioKB-ChEBI.",
    description=description,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    uvicorn.run(
        app="biokb_chebi.api.main:app",
        host=host,
        port=port,
        log_level="warning",
    )


def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(HTTPBasic()),
) -> None:
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


@app.post(
    path="/import_data/",
    response_model=dict[str, int],
    tags=[Tag.DBMANAGE],
)
async def import_data(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    force_download: bool = Query(
        False,
        description=(
            "Whether to re-download data files even if they already exist,"
            " ensuring the newest version."
        ),
    ),
    keep_files: bool = Query(
        True,
        description=(
            "Whether to keep the downloaded files"
            " after importing them into the database."
        ),
    ),
) -> dict[str, int]:
    """Download data (if not exists) and load in database.

    Can take up to 15 minutes to complete.
    """
    try:
        dbm = manager.DbManager()
        result = dbm.import_data(force_download=force_download, keep_files=keep_files)
    except Exception as e:
        logger.error(f"Error importing data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing data. {e}",
        ) from e
    return result


@app.get("/export_ttls/", tags=[Tag.DBMANAGE])
async def get_report(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    force_create: bool = Query(
        False,
        description="Whether to re-generate the TTL files even if they already exist.",
    ),
) -> FileResponse:

    file_path = ZIPPED_TTLS_PATH
    if not os.path.exists(file_path) or force_create:
        try:
            TurtleCreator().create_ttls()
        except Exception as e:
            logger.error(f"Error generating TTL files: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating TTL files. Data already imported?",
            ) from e
    return FileResponse(
        path=file_path, filename="chebi_ttls.zip", media_type="application/zip"
    )


@app.get("/import_neo4j/", tags=[Tag.DBMANAGE])
async def import_neo4j(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    uri: str | None = Query(
        NEO4J_URI,
        description="The Neo4j URI. If not provided, "
        "the default from environment variable is used.",
    ),
    user: str | None = Query(
        NEO4J_USER,
        description="The Neo4j user. If not provided,"
        " the default from environment variable is used.",
    ),
    password: str | None = Query(
        NEO4J_PASSWORD,
        description="The Neo4j password. If not provided,"
        " the default from environment variable is used.",
    ),
) -> dict[str, str]:
    """Import RDF turtle files in Neo4j."""
    try:
        if not os.path.exists(ZIPPED_TTLS_PATH):
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail=(
                    "Zipped TTL files not found. Please "
                    "generate them first using /export_ttls/ endpoint."
                ),
            )
        importer = Neo4jImporter(neo4j_uri=uri, neo4j_user=user, neo4j_pwd=password)
        importer.import_ttls()
    except Exception as e:
        logger.error(f"Error importing data into Neo4j: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing data into Neo4j: {e}",
        ) from e
    return {"status": "Neo4j import completed successfully."}


# tag: Compound
# ========================


@app.get("/compounds/", response_model=schemas.CompoundSearchResults, tags=[Tag.CHEBI])
async def search_compounds(
    search: schemas.CompoundSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """
    Search compounds.
    """
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Compound,
        session=session,
        limit=limit,
        offset=offset,
    )


# tag: Chemical Data
# ========================


@app.get(
    "/chemical_data/",
    response_model=schemas.ChemicalDataSearchResults,
    tags=[Tag.CHEBI],
)
async def search_chemical_data(
    search: schemas.ChemicalDataSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
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
        session=session,
        limit=limit,
        offset=offset,
    )


# tag: DatabaseAccession
# ========================


@app.get(
    "/database_accession/",
    response_model=schemas.DatabaseAccessionSearchResults,
    tags=[Tag.CHEBI],
)
async def search_database_accession(
    search: schemas.DatabaseAccessionSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """Search Database Accession."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.DatabaseAccession,
        session=session,
        limit=limit,
        offset=offset,
    )


# tag: Name
# ========================
@app.get(
    "/name/",
    response_model=schemas.NameSearchResults,
    tags=[Tag.CHEBI],
)
async def search_name(
    search: schemas.NameSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """Search Name."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Name,
        session=session,
        limit=limit,
        offset=offset,
    )


# tag: RelationType
# ========================


@app.get(
    "/relation_type/",
    response_model=schemas.RelationTypeSearchResults,
    tags=[Tag.CHEBI],
)
async def search_relation_type(
    search: schemas.RelationTypeSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """Search Relation type."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.RelationType,
        session=session,
        limit=limit,
        offset=offset,
    )


# tag: Relation
# ========================


@app.get(
    "/relation/",
    response_model=schemas.RelationSearchResults,
    tags=[Tag.CHEBI],
)
async def search_relation(
    search: schemas.RelationSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """Search Relation."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Relation,
        session=session,
        limit=limit,
        offset=offset,
    )


# tag: Reference
# ========================
@app.get(
    "/reference/",
    response_model=schemas.ReferenceSearchResults,
    tags=[Tag.CHEBI],
)
async def search_reference(
    search: schemas.ReferenceSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """Search Reference."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Reference,
        session=session,
        limit=limit,
        offset=offset,
    )


# tag: Source
# ========================
@app.get(
    "/source/",
    response_model=schemas.SourceSearchResults,
    tags=[Tag.CHEBI],
)
async def search_source(
    search: schemas.SourceSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """Search Source."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Source,
        session=session,
        limit=limit,
        offset=offset,
    )


# tag: Status
# ========================
@app.get(
    "/status/",
    response_model=schemas.StatusSearchResults,
    tags=[Tag.CHEBI],
)
async def search_status(
    search: schemas.StatusSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """Search Status."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Status,
        session=session,
        limit=limit,
        offset=offset,
    )


# tag: Structure
# ========================
@app.get(
    "/structure/",
    response_model=schemas.StructureSearchResults,
    tags=[Tag.CHEBI],
)
async def search_structure(
    search: schemas.StructureSearch = Depends(),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    session: Session = Depends(get_session),
) -> SASearchResults | dict[str, str]:
    """Search Structure."""
    return build_dynamic_query(
        search_obj=search,
        model_cls=models.Structure,
        session=session,
        limit=limit,
        offset=offset,
    )
