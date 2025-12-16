import logging
import os
import re
from typing import Optional

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker

from biokb_chebi.constants.basic import DATA_FOLDER, DB_DEFAULT_CONNECTION_STR
from biokb_chebi.db.importer import DatabaseImporter
from biokb_chebi.db.models import Base

logger = logging.getLogger(__name__)


class DbManager:
    def __init__(
        self,
        engine: Optional[Engine] = None,
        data_folder: Optional[str] = None,
    ):
        connection_str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.__engine = engine if engine else create_engine(str(connection_str))

        logger.info("Engine %s", self.__engine)
        self.Session = sessionmaker(bind=self.__engine)
        self.__data_folder = data_folder or DATA_FOLDER

    def create_empty_db(self) -> None:
        """Creates an empty database by delete the old and recreate a new."""
        Base.metadata.drop_all(self.__engine)
        Base.metadata.create_all(self.__engine)

    def import_data(self, redownload: bool = False) -> dict[str, int]:
        db_importer = DatabaseImporter(
            engine=self.__engine, data_folder=self.__data_folder
        )
        return db_importer.import_db(redownload=redownload)
