"""MySQL database importer module."""

import logging
import os
from typing import Dict, Optional

import pandas as pd
import requests
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from tqdm import tqdm

from biokb_chebi.constants import (
    BASE_URL_DOWNLOAD,
    CHEMICAL_DATA_FILE,
    COMMENT_FILE,
    COMPOUND_FILE,
    DATA_FOLDER,
    DATABASE_ACCESSION_FILE,
    DB_DEFAULT_CONNECTION_STR,
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


class DbManager:
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
    ):
        """Init DatabaseImporter

        Args:
            data_folder_path (Optional[str]): Folder downloadfiles. Defaults to None.
            engine (Optional[Engine]): SQLAlchemy engine. Defaults to None.
            redownload (bool): True if the data should be downloaded
                               even if they already exists. Default False.
        """
        self.__data_folder: str = DATA_FOLDER
        connection_str: str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.__engine: Engine = engine if engine else create_engine(str(connection_str))
        self.Session: sessionmaker[Session] = sessionmaker(bind=self.__engine)

    def _set_data_folder(self, data_folder: str) -> None:
        """Sets the data folder path.

        This is mainly for testing purposes.
        """
        self.__data_folder = data_folder

    def __create_empty_db(self) -> None:
        """Creates an empty database by delete the old and recreate a new."""
        Base.metadata.drop_all(self.__engine)
        Base.metadata.create_all(self.__engine)

    def import_data(
        self, force_download: bool = False, keep_files: bool = False
    ) -> Dict[str, int]:
        """Import all data in MySQL database.

        Returns:
            bool: Returns True
        """
        # Always remove a log if a new import starts
        print(self.__data_folder)
        self.__download_data(force_download=force_download)
        self.__create_empty_db()
        result_dict = self.__insert_data()
        if not keep_files:
            for file_name in self.table_file_dict.values():
                path_to_delete = os.path.join(self.__data_folder, file_name)
                if os.path.exists(path_to_delete):
                    os.remove(path_to_delete)
                    logger.info("Removed file %s", path_to_delete)
        return result_dict

    def __download_data(self, force_download: bool = False) -> None:
        """Downloads chebi data from it's ftp server.

        Args:
            redownload (bool, optional): If True, will force download the data, even if
            files already exist. If False, it will skip the downloading part if files
            already exist locally. Defaults to False.
        """
        logger.info("Start download of data")
        files_exists = 0
        files_downloaded = 0
        for file_name in tqdm(self.table_file_dict.values()):
            path_to_download = os.path.join(self.__data_folder, file_name)
            if os.path.exists(path_to_download) and not force_download:
                files_exists += 1
                continue
            url = f"{BASE_URL_DOWNLOAD}/{file_name}"

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(path_to_download, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            files_downloaded += 1
        logger.info("Files already exist: %d", files_exists)
        logger.info("Files downloaded: %d", files_downloaded)

    def __insert_data(self) -> Dict[str, int]:
        """Insert data in chebi db tables.

        Returns:
            Dict[str, int]: table=key and number of inserted=value
        """
        logger.info("Insert data in database")

        inserted = {}

        for table_name, file_name in tqdm(self.table_file_dict.items()):
            file_path = os.path.join(self.__data_folder, file_name)

            usecols = None
            if table_name == models.Structure.__tablename__:
                columns = pd.read_csv(file_path, sep="\t", nrows=1).columns.to_list()
                usecols = [x for x in columns if x != "molfile"]

            parse_dates = []
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
                for col in parse_dates:
                    df[col] = pd.to_datetime(df[col], utc=True)
                df.to_sql(
                    table_name,
                    self.__engine,
                    index=False,
                    if_exists="append",
                )
                inserted[table_name] += df.shape[0]

        return inserted
