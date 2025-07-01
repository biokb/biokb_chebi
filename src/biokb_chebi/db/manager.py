import logging
import os
from typing import Optional

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker

from biokb_chebi.constants.basic import DB_DEFAULT_CONNECTION_STR
from biokb_chebi.db.importer import DatabaseImporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DbManager:
    def __init__(
        self,
        engine: Optional[Engine] = None,
    ):
        connection_str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.engine = engine if engine else create_engine(str(connection_str))
        if self.engine.dialect.name == "sqlite":
            with self.engine.connect() as connection:
                connection.execute(text("pragma foreign_keys=ON"))

        logger.info("Engine %s", self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def import_data(self):
        return DatabaseImporter(self.engine).import_db()
