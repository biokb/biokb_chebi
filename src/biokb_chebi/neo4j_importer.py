"""Neo4j importer module."""

import logging
import os
import shutil
import zipfile

from biokb_chebi.manager import Neo4jDatabase
from rdflib import Graph
from rdflib_neo4j import HANDLE_VOCAB_URI_STRATEGY, Neo4jStore, Neo4jStoreConfig
from tqdm import tqdm
from urllib.request import urlretrieve

from biokb_chebi.constants.basic import DATA_FOLDER, ZIPPED_TTLS_PATH
from biokb_chebi.constants.chebi import BASIC_NODE_LABEL
from typing import Optional

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger: logging.Logger = logging.getLogger(name=__name__)


class Neo4jImporter:
    """Neo4j importer class."""

    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_pwd: Optional[str] = None,
        path_or_url: Optional[str] = None,
        config_file: Optional[str] = None,
        delete_existing_graph: bool = False,
    ) -> None:
        """Init Neo4jImporter

        Args:
            neo4j_uri (str): Neo4j URI
            neo4j_user (str): Neo4j user
            neo4j_pwd (str): Neo4j password
            path_or_url (str | None, optional): Local path or URL to zipped file with ttls. Defaults to None.
            delete_existing_graph (bool, optional): If True deletes ChEBI graph before import. Defaults to False.

        Raises:
            FileExistsError: _description_
        """
        self.db = Neo4jDatabase(
            user=neo4j_user,
            password=neo4j_pwd,
            uri=neo4j_uri,
            config_file=config_file,
        )

        self.is_url = False
        if path_or_url:
            self.path_or_url = path_or_url
            if self.path_or_url.startswith("http"):
                self.is_url = True
        else:
            self.path_or_url = ZIPPED_TTLS_PATH

        if not self.is_url and not os.path.exists(self.path_or_url):
            raise FileExistsError(f"File {path_or_url} not exists.")

        self.turtles_folder = os.path.join(DATA_FOLDER, "ttls")

        self.delete_existing_graph = delete_existing_graph

    def extract_turtles_zip(self) -> None:
        """Extract the zipped turtle files."""
        logger.info("Extract the zipped turtle files.")

        if self.is_url:
            download_path = os.path.join(DATA_FOLDER, "ttls_from_url.zip")
            urlretrieve(self.path_or_url, download_path)
            self.path_or_url = download_path

        with zipfile.ZipFile(self.path_or_url, "r") as zip_ref:
            zip_ref.extractall(self.turtles_folder)

    def _delete_existing_graph(self) -> None:
        """Delete an existing ChEBI graph in Neo4J."""
        logger.info("Delete an existing graph in Neo4J.")
        with self.db.driver.session() as session:
            cypher = f"MATCH (n:{BASIC_NODE_LABEL}) CALL {{ WITH n DETACH DELETE n}} IN TRANSACTIONS OF 1000 ROWS"
            session.run(cypher)

    def import_ttls(self) -> bool:
        """Import all turtle file in Neo4J."""
        logger.info("Start importing all turtle file in Neo4J.")
        self.extract_turtles_zip()
        if self.delete_existing_graph:
            self._delete_existing_graph()
        with self.db.driver.session() as session:
            cypher = (
                "CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS "
                "FOR (r:Resource) REQUIRE r.uri IS UNIQUE"
            )
            session.run(cypher)
            self.db.driver.close()

        auth_data = {
            "uri": self.db.uri,
            "database": self.db.db_name,
            "user": self.db.user,
            "pwd": self.db.password,
        }

        config = Neo4jStoreConfig(
            auth_data=auth_data,
            custom_prefixes={},
            handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.IGNORE,
            batching=True,
        )

        neo4j_db = Graph(store=Neo4jStore(config=config))

        ttl_files = [x for x in os.listdir(self.turtles_folder) if x.endswith(".ttl")]
        for ttl_file in tqdm(ttl_files, desc="Import ttls into Neo4j"):
            ttl_path = os.path.join(self.turtles_folder, ttl_file)
            neo4j_db.parse(ttl_path, format="ttl")
        neo4j_db.close(True)

        shutil.rmtree(self.turtles_folder)
        return True
