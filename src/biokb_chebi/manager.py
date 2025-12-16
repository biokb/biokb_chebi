"""Database manager module."""

import configparser
import logging
import os
from typing import Optional

from neo4j import Driver, GraphDatabase
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import PoolProxiedConnection

from biokb_chebi.constants.basic import DEFAULT_CONFIG_PATH, LOGS_FOLDER

log_file = os.path.join(LOGS_FOLDER, "importer.log")

if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
    filename=log_file,
)
logger: logging.Logger = logging.getLogger(__name__)


class MySQLDatabase:
    """Database class."""

    def __init__(
        self,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = "127.0.0.1",
        port: Optional[int] = 3306,
        db_name: Optional[str] = None,
        config_file: str | None = None,
    ) -> None:
        """Init MySQLDatabase"""
        if user and password and host and port and db_name:
            self.user, self.password, self.host, self.port, self.db_name = (
                user,
                password,
                host,
                port,
                db_name,
            )
            self.__engine = create_engine(
                f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
            )

        else:
            self.config_file = config_file or DEFAULT_CONFIG_PATH

            if os.path.exists(self.config_file):
                config = configparser.ConfigParser()
                config.read(self.config_file)
                conf = config["MYSQL"]
                self.user, self.password, self.host, self.port, self.db_name = (
                    conf["user"],
                    conf["password"],
                    conf["host"],
                    int(conf["port"]),
                    conf["db_name"],
                )
                self.__engine = create_engine(
                    f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
                )

            else:
                msg = (
                    "Neither MySQL access data (user and password) or "
                    f"path to config file are given nor default config file ({DEFAULT_CONFIG_PATH}) exists."
                )
                logger.critical(msg)
                raise Exception(msg)

    @property
    def engine(self) -> Engine:
        """Get SQLAlchemy engine."""
        return self.__engine

    @property
    def connection(self) -> PoolProxiedConnection:
        """Return SQLAlchemy raw connection."""
        return self.engine.raw_connection()


class Neo4jDatabase:
    """Neo4jDatabase class."""

    def __init__(
        self,
        user: Optional[str] = "neo4j",
        password: Optional[str] = None,
        uri: Optional[str] = "neo4j://localhost:7687",
        db_name: Optional[str] = "neo4j",
        config_file: Optional[str] = None,
    ) -> None:
        """Init Neo4j database class

        Args:
            neo4j_user (Optional[str]): Neo4j user
            neo4j_password (Optional[str]): Neo4j password
            neo4j_uri (Optional[str]): Neo4j URI
            config_file (Optional[str]): path to config file
        """
        default_config_exists = os.path.exists(DEFAULT_CONFIG_PATH)

        if bool(user and password and db_name) and isinstance(uri, str):
            self.user = user
            self.password = password
            self.uri = uri
            self.db_name = db_name
            self.__neo4j_driver = GraphDatabase.driver(
                uri=self.uri, auth=(self.user, self.password), database=self.db_name
            )
        elif config_file or default_config_exists:
            self.__config_file = config_file or DEFAULT_CONFIG_PATH
            config = configparser.ConfigParser()
            config.read(self.__config_file)
            conf = config["NEO4J"]
            self.user, self.password, self.uri, self.db_name = (
                conf["user"],
                conf["password"],
                conf["uri"],
                conf["db_name"],
            )
            self.__neo4j_driver = GraphDatabase.driver(
                uri=self.uri, auth=(self.user, self.password), database=self.db_name
            )
        else:
            msg = (
                "Neither Neo4j access data (user and password and uri) or "
                f"path to config file are given nor default config file ({DEFAULT_CONFIG_PATH}) exists."
            )
            logger.critical(msg)
            raise Exception(msg)

    @property
    def driver(self) -> Driver:
        """Get Neo4j driver."""
        return self.__neo4j_driver
