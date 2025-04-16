"""Useful methods for Create, Read, Update and Delete."""

import os
from typing import Optional

from sqlalchemy import create_engine

from biokb_chebi.constants.basic import EXPORT_FOLDER
from biokb_chebi.db.importer import DatabaseImporter
from biokb_chebi.manager import MySQLDatabase
from biokb_chebi.neo4j_importer import Neo4jImporter
from biokb_chebi.rdf.turtle import TurtleCreator


def import_mysql(
    mysql_password: Optional[str] = None,
    mysql_user: Optional[str] = None,
    mysql_database: Optional[str] = None,
    mysql_host: Optional[str] = None,
    mysql_port: Optional[int] = None,
    data_folder: Optional[str] = None,
    config_file: Optional[str] = None,
    redownload: bool = False,
) -> None:
    if mysql_password:
        engine = create_engine(
            f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        )
    else:
        engine = MySQLDatabase(config_file=config_file).engine

    importer = DatabaseImporter(
        engine=engine, data_folder=data_folder, redownload=redownload
    )
    importer.import_db()


def create_ttls(
    mysql_user: Optional[str] = None,
    mysql_password: Optional[str] = None,
    mysql_database: Optional[str] = None,
    mysql_host: Optional[str] = None,
    mysql_port: Optional[int] = None,
    export_folder: Optional[str] = None,
    config_file: Optional[str] = None,
) -> None:
    """_summary_

    Args:
        mysql_user (str): MySQL user
        mysql_password (str): MySQL password
        mysql_database (str): MySQL database
        mysql_host (str): MySQL host
        mysql_port (int): MySQL port
        export_folder (str): Folder to export the ttls file
        silent (bool): If True silent, no output
    """
    if mysql_password:
        engine = create_engine(
            f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        )
    else:
        engine = MySQLDatabase(config_file=config_file).engine

    turtle_creator = TurtleCreator(engine=engine, export_to_folder=export_folder)
    turtle_creator.create_all_ttls()


def import_all(
    neo4j_pwd: Optional[str] = None,
    mysql_password: Optional[str] = None,
    mysql_user: Optional[str] = None,
    mysql_host: Optional[str] = None,
    mysql_port: Optional[int] = None,
    mysql_database: Optional[str] = None,
    neo4j_user: Optional[str] = None,
    neo4j_uri: Optional[str] = None,
    data_folder: Optional[str] = None,
    ttl_export_folder: Optional[str] = None,
    config_file: Optional[str] = None,
    delete_existing_graph: bool = True,
) -> None:
    """Download, import data in database, export RDF turtle files and import turtle files in Neo4j

    Args:
        neo4j_pwd (str): Neo4J password.
        mysql_password (str): MySQL password.
        mysql_user (str, optional): MySQL user. Defaults to "biokb_chebi_user".
        mysql_host (str, optional): MySQL host. Defaults to "localhost".
        mysql_port (int, optional): MySQL port. Defaults to 3306.
        mysql_database (str, optional): MySQL database name. Defaults to "biokb_chebi".
        neo4j_user (str, optional): Neo4J user. Defaults to "neo4j".
        neo4j_uri (str, optional): Neo4J URI. Defaults to "neo4j://localhost:7687".
        data_folder (str, optional): path to data folder.
        ttl_export_folder (str, optional): folder where zipped file with turtles is created.
        config_file (str, optional): path to config file.
        delete_existing_graph (bool, optional): If True graph will be deleted. Defaults to True.
    """
    if mysql_password:
        engine = create_engine(
            f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        )
    else:
        engine = MySQLDatabase(config_file=config_file).engine

    importer = DatabaseImporter(engine=engine, data_folder=data_folder)
    importer.import_db()

    turtle_creator = TurtleCreator(engine=engine, export_to_folder=ttl_export_folder)
    turtle_creator.create_all_ttls()

    if not ttl_export_folder:
        ttl_export_folder = EXPORT_FOLDER

    neo4j_importer = Neo4jImporter(
        neo4j_pwd=neo4j_pwd,
        neo4j_user=neo4j_user,
        neo4j_uri=neo4j_uri,
        path_or_url=os.path.join(ttl_export_folder, "ttls.zip"),
        delete_existing_graph=delete_existing_graph,
    )
    neo4j_importer.import_ttls()
