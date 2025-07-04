"""MySQL database importer module."""

import logging
import os
from ftplib import FTP
from typing import Dict, Optional

import pandas as pd
from sqlalchemy.engine.base import Engine
from tqdm import tqdm

from biokb_chebi.constants.basic import DATA_FOLDER, LOGS_FOLDER
from biokb_chebi.constants.chebi import (
    CHEMICAL_DATA_FILE,
    COMMENT_FILE,
    COMPOUND_FILE,
    DATABASE_ACCESSION_FILE,
    FTP_DIR,
    FTP_SERVER,
    INCHI_FILE,
    NAME_FILE,
    REFERENCE_FILE,
    RELATION_FILE,
)
from biokb_chebi.db import models
from biokb_chebi.db.models import Base

log_file = os.path.join(LOGS_FOLDER, "importer.log")

if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
    filename=log_file,
)
logger: logging.Logger = logging.getLogger(__name__)


class DatabaseImporter:
    """Database import for ChEBI data."""

    table_file_dict: dict[str, str] = {
        models.Compound.__tablename__: COMPOUND_FILE,
        models.ChemicalData.__tablename__: CHEMICAL_DATA_FILE,
        models.Comment.__tablename__: COMMENT_FILE,
        models.DatabaseAccession.__tablename__: DATABASE_ACCESSION_FILE,
        models.Inchi.__tablename__: INCHI_FILE,
        models.Name.__tablename__: NAME_FILE,
        models.Relation.__tablename__: RELATION_FILE,
        models.Reference.__tablename__: REFERENCE_FILE,
    }

    def __init__(
        self,
        engine: Engine,
        data_folder: Optional[str] = None,
        redownload: bool = False,
    ):
        """Init DatabaseImporter

        Args:
            data_folder_path (Optional[str], optional): Folder where to store download files. Defaults to None.
            engine (Optional[Engine], optional): SQLAlchemy engine. Defaults to None.
            redownload (bool): True if the data should be downaloded even if they already exists. Default False.
        """
        self.__data_folder = data_folder or DATA_FOLDER
        self.engine = self.check_is_mysql_or_mariadb(engine)
        self.redownload = redownload

    def check_is_mysql_or_mariadb(self, engine: Engine) -> Engine:
        """Check if engine is a the SQLAlchemy engine and uses MySQL or MariaDb

        Args:
            engine (Engine): variable check for isstance

        Raises:
            Exception: Raises exception if not SQLAlchemy engine or not MySQL or MariaDb
        """
        if not isinstance(engine, Engine):
            msg = "engine is not a SQLAchemy Engine"
            logger.critical(msg)
            raise Exception(msg)
        elif engine.dialect.name not in ("mysql", "mariadb"):
            msg = "SQLAlchemy Engine has to use MySQL or MariaDb"
            logger.critical(msg)
            raise Exception(msg)
        return engine

    def set_data_folder(self, path_to_datafolder: str) -> None:
        """Set the data folder."""
        self.__data_folder = path_to_datafolder

    def create_empty_db(self) -> None:
        """Creates an empty database by delete the old and recreate a new."""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def import_db(self) -> Dict[str, int]:
        """Import all data in MySQL database.

        Returns:
            bool: Returns True
        """
        # Always remove a log if a new import starts
        self.download_data(redownload=self.redownload)
        self.create_empty_db()
        return self.insert_data()

    def get_ftp_client(self) -> FTP:
        """Get an FTP client.

        Returns:
            FTP: FTP client
        """
        ftp = FTP(FTP_SERVER)
        ftp.login()
        ftp.set_pasv(True)
        ftp.cwd(FTP_DIR)
        return ftp

    def download_data(self, redownload: bool = False) -> None:
        """Downloads chebi data from it's ftp server.

        Args:
            redownload (bool, optional): If True, will force download the data, even if
            files already exist. If False, it will skip the downloading part if files already
            exist locally. Defaults to False.
        """
        ftp: Optional[FTP] = None

        for file_name in tqdm(
            self.table_file_dict.values(), desc="Download ChEBI files."
        ):
            path_to_download = os.path.join(self.__data_folder, file_name)

            if not redownload and os.path.exists(path_to_download):
                logger.info(f"Skipped: {path_to_download} (File already exists)")
            else:
                try:
                    ftp = ftp or self.get_ftp_client()
                    with open(path_to_download, "wb") as file:
                        ftp.retrbinary("RETR " + file_name, file.write)
                    logger.info(f"Downloaded: {file_name}")
                except Exception as e:
                    logger.critical(f"Error downloading {file_name}: {e}")
                    raise Exception(e)
        if ftp:
            ftp.quit()

    def insert_data(self) -> Dict[str, int]:
        """Insert data in chebi db tables.

        Returns:
            Dict[str, int]: Dictionary with table as key and number of inserted rows as value
        """
        logger.info("Insert data in database")

        inserted = {}

        file_path_compound = os.path.join(self.__data_folder, COMPOUND_FILE)
        df_compounds = pd.read_csv(
            file_path_compound, sep="\t", encoding="unicode_escape"
        )
        df_compound_ids = df_compounds[["ID"]]
        del df_compounds

        for table_name, file_name in tqdm(
            self.table_file_dict.items(), desc="Insert ChEBI data in database"
        ):
            file_path = os.path.join(self.__data_folder, file_name)
            encoding = (
                "ISO-8859-1" if table_name == "chebi_reference" else "unicode_escape"
            )

            dfs = pd.read_csv(
                file_path,
                sep="\t",
                encoding=encoding,
                low_memory=False,
                # on_bad_lines="skip",
                chunksize=100000,
            )

            inserted[table_name] = 0

            for df in dfs:
                df.columns = df.columns.str.lower()

                if table_name == models.Inchi.__tablename__:
                    df.index += 1
                    df.index.rename("id", inplace=True)
                    df.rename(columns={"chebi_id": "compound_id"}, inplace=True)

                if "compound_id" in df.columns:
                    df = (
                        df_compound_ids.rename(columns={"ID": "compound_id"})
                        .set_index("compound_id")
                        .join(df.set_index("compound_id"), how="inner")
                        .reset_index()
                    )

                if "init_id" in df.columns:
                    df = (
                        df_compound_ids.rename(columns={"ID": "init_id"})
                        .set_index("init_id")
                        .join(df.set_index("init_id"), how="inner")
                        .reset_index()
                    )

                if "final_id" in df.columns:
                    df = (
                        df_compound_ids.rename(columns={"ID": "final_id"})
                        .set_index("final_id")
                        .join(df.set_index("final_id"), how="inner")
                        .reset_index()
                    )
                df.to_sql(table_name, self.engine, index=False, if_exists="append")
                inserted[table_name] += df.shape[0]

        return inserted
