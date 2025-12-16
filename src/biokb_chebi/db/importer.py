"""MySQL database importer module."""

import logging
import os
from typing import Dict, Optional

import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from tqdm import tqdm

from biokb_chebi.constants.basic import (
    DATA_FOLDER,
    DB_DEFAULT_CONNECTION_STR,
    LOGS_FOLDER,
)
from biokb_chebi.constants.chebi import (
    BASE_URL_DOWNLOAD,
    CHEMICAL_DATA_FILE,
    COMMENT_FILE,
    COMPOUND_FILE,
    DATABASE_ACCESSION_FILE,
    NAME_FILE,
    REFERENCE_FILE,
    RELATION_FILE,
    RELATION_TYPE_FILE,
    SOURCE_FILE,
    STATUS_FILE,
    STRUCTURE_FILE,
)
from biokb_chebi.db import models
from biokb_chebi.db.models import Base

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger: logging.Logger = logging.getLogger(__name__)


class DatabaseImporter:
    """Database import for ChEBI data."""

    table_file_dict: dict[str, str] = {
        models.Status.__tablename__: STATUS_FILE,
        models.Source.__tablename__: SOURCE_FILE,
        models.RelationType.__tablename__: RELATION_TYPE_FILE,
        models.Compound.__tablename__: COMPOUND_FILE,
        models.Structure.__tablename__: STRUCTURE_FILE,
        models.ChemicalData.__tablename__: CHEMICAL_DATA_FILE,
        models.Comment.__tablename__: COMMENT_FILE,
        models.DatabaseAccession.__tablename__: DATABASE_ACCESSION_FILE,
        models.Name.__tablename__: NAME_FILE,
        models.Relation.__tablename__: RELATION_FILE,
        models.Reference.__tablename__: REFERENCE_FILE,
    }

    def __init__(
        self,
        engine: Optional[Engine] = None,
        data_folder: Optional[str] = None,
    ):
        """Init DatabaseImporter

        Args:
            data_folder_path (Optional[str], optional): Folder where to store download files. Defaults to None.
            engine (Optional[Engine], optional): SQLAlchemy engine. Defaults to None.
            redownload (bool): True if the data should be downaloded even if they already exists. Default False.
        """
        self.__data_folder = data_folder or DATA_FOLDER
        connection_str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.__engine = engine if engine else create_engine(str(connection_str))

    def create_empty_db(self) -> None:
        """Creates an empty database by delete the old and recreate a new."""
        Base.metadata.drop_all(self.__engine)
        Base.metadata.create_all(self.__engine)

    def import_db(self, redownload: bool = False) -> Dict[str, int]:
        """Import all data in MySQL database.

        Returns:
            bool: Returns True
        """
        # Always remove a log if a new import starts
        self.download_data(redownload=redownload)
        self.create_empty_db()
        return self.insert_data()

    def download_data(self, redownload: bool = False) -> None:
        """Downloads chebi data from it's ftp server.

        Args:
            redownload (bool, optional): If True, will force download the data, even if
            files already exist. If False, it will skip the downloading part if files already
            exist locally. Defaults to False.
        """
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER, exist_ok=True)

        for file_name in tqdm(
            self.table_file_dict.values(), desc="Download ChEBI files."
        ):
            path_to_download = os.path.join(self.__data_folder, file_name)
            if os.path.exists(path_to_download) and not redownload:
                logger.info(
                    "File %s already exists. Skipping download.", path_to_download
                )
                continue
            url = f"{BASE_URL_DOWNLOAD}/{file_name}"

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(path_to_download, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            logger.info("Downloaded file %s", path_to_download)

    def insert_data(self) -> Dict[str, int]:
        """Insert data in chebi db tables.

        Returns:
            Dict[str, int]: Dictionary with table as key and number of inserted rows as value
        """
        logger.info("Insert data in database")

        inserted = {}

        for table_name, file_name in self.table_file_dict.items():
            logger.info(f"Inserting data from file {file_name}")
            file_path = os.path.join(self.__data_folder, file_name)

            usecols = None
            parse_dates = None
            if table_name == models.Structure.__tablename__:
                columns = pd.read_csv(file_path, sep="\t", nrows=1).columns.to_list()
                usecols = [x for x in columns if x != "molfile"]
            if table_name == models.Compound.__tablename__:
                parse_dates = ["release_date", "modified_on"]

            dfs = pd.read_csv(
                file_path,
                sep="\t",
                low_memory=False,
                chunksize=100000,
                usecols=usecols,
                parse_dates=parse_dates,
            )

            inserted[table_name] = 0

            for df in dfs:

                df.to_sql(table_name, self.__engine, index=False, if_exists="append")
                inserted[table_name] += df.shape[0]

        return inserted
