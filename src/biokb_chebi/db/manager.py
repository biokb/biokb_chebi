import logging
import os
from typing import Optional

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker

from biokb_chebi.constants.basic import DB_DEFAULT_CONNECTION_STR, DATA_FOLDER
from biokb_chebi.db.importer import DatabaseImporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DbManager:
    def __init__(
        self,
        engine: Optional[Engine] = None,
        data_folder: Optional[str] = None,
    ):
        connection_str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.engine = engine if engine else create_engine(str(connection_str))
        if self.engine.dialect.name == "sqlite":
            with self.engine.connect() as connection:
                connection.execute(text("pragma foreign_keys=ON"))

        logger.info("Engine %s", self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.__data_folder = data_folder or DATA_FOLDER


    def set_data_folder(self, path_to_datafolder: str) -> None:
        """Set the data folder."""
        self.__data_folder = path_to_datafolder

    def import_data(self):
        db_importer = DatabaseImporter(engine=self.engine)
        db_importer.set_data_folder(self.__data_folder)
        return db_importer.import_db()
