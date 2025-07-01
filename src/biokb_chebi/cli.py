"""Command line module."""

import logging
import re
from typing import Optional

import click
from sqlalchemy import create_engine

from biokb_chebi.constants.basic import (
    DATA_FOLDER,
    DEFAULT_CONFIG_PATH,
    EXPORT_FOLDER,
    ZIPPED_TTLS_PATH,
)
from biokb_chebi.crud import import_all
from biokb_chebi.db.importer import DatabaseImporter
from biokb_chebi.manager import MySQLDatabase
from biokb_chebi.neo4j_importer import Neo4jImporter
from biokb_chebi.rdf.turtle import TurtleCreator


# we are creating a group
@click.group()
def main() -> None:
    """Main group of cli."""
    pass


###########################################################################################################
# import-data
###########################################################################################################


@main.command(
    help=(
        "Downloads and imports ChEBI data in MySQL.\n"
        "\nExamples:\n"
        f"\nIf you have saved the settings in {DEFAULT_CONFIG_PATH}\n"
        "\n\tbiokb_chebi import-data\n"
        "\nwith different location of config.ini\n"
        "\n\tbiokb_chebi import-data --config_file /path/to/config.ini\n"
        "\nwithout any config.ini\n"
        "\n\tbiokb_chebi import-data -mu my_user -mp my_password -mh localhost -mo 3306 -md my_database_name\n"
    )
)
@click.option(
    "-mu",
    "--mysql_user",
    help="MySQL user.",
    show_default=True,
    default="biokb_chebi_user",
)
@click.option("-mp", "--mysql_password", help="MySQL password.", default=None)
@click.option(
    "-md",
    "--mysql_database",
    default="biokb_chebi",
    show_default=True,
    help="MySQL database.",
)
@click.option(
    "-mh",
    "--mysql_host",
    default="127.0.0.1",
    show_default=True,
    help="MySQL host.",
)
@click.option(
    "-mo",
    "--mysql_port",
    default=3306,
    show_default=True,
    help="MySQL port.",
    type=int,
)
@click.option(
    "-df",
    "--data_folder",
    default=DATA_FOLDER,
    show_default=True,
    help="Path to data folder.",
)
@click.option(
    "-cf",
    "--config_file",
    default=DEFAULT_CONFIG_PATH,
    show_default=True,
    help="Path to config.ini file.",
)
@click.option(
    "-rd",
    "--redownload",
    is_flag=True,
    default=False,
    show_default=True,
    help="Set if you want to redownload the ChEBI data.",
)
def import_data(
    mysql_user: str,
    mysql_password: Optional[str],
    mysql_database: str,
    mysql_host: str,
    mysql_port: int,
    data_folder: str,
    config_file: str,
    redownload: bool,
) -> None:
    """Import the data from ChEBI.

    Args:
        mysql_user (str): MySQL user
        mysql_password (str, optional): MySQL password
        mysql_database (str): MySQL database
        mysql_host (str): MySQL host
        mysql_port (int): MySQL host
        data_folder (str): Path to data folder
        config_file (str): Path to config.ini file
    """
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


###########################################################################################################
# create-ttls
###########################################################################################################


@main.command(
    help=(
        "Create RDF triples as turtle files and zipped it"
        "\nExamples:\n"
        f"\nIf you have saved the settings in {DEFAULT_CONFIG_PATH}\n"
        "\n\tbiokb_chebi import-data\n"
        "\n\nExample:\n\nbiokb_chebi create-ttls -mu biokb_chebi_user -mp biokb_chebi_password -mo 3307"
    )
)
@click.option(
    "-mu", "--mysql_user", help="MySQL user.", show_default=True, default="biokb_chebi"
)
@click.option(
    "-mp",
    "--mysql_password",
    help="MySQL password.",
)
@click.option(
    "-md",
    "--mysql_database",
    default="biokb",
    show_default=True,
    help="MySQL database.",
)
@click.option(
    "-mh",
    "--mysql_host",
    default="127.0.0.1",
    show_default=True,
    help="MySQL host.",
)
@click.option(
    "-mo",
    "--mysql_port",
    default=3306,
    show_default=True,
    help="MySQL port.",
    type=int,
)
@click.option(
    "-e",
    "--export_folder",
    default=EXPORT_FOLDER,
    show_default=True,
    help="Optional. Local path export folder.",
)
@click.option(
    "-cf",
    "--config_file",
    default=DEFAULT_CONFIG_PATH,
    show_default=True,
    help="Path to config.ini file.",
)
@click.option(
    "-s",
    "--silent",
    is_flag=True,
    default=False,
    help="If been set, execute silent.",
)
def create_ttls(
    mysql_user: str,
    mysql_password: str,
    mysql_database: str,
    mysql_host: str,
    mysql_port: int,
    export_folder: str,
    config_file: str,
    silent: bool,
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

    if not silent:
        logging.basicConfig(level=logging.INFO)
    turtle_creator = TurtleCreator(engine=engine, export_to_folder=export_folder)
    turtle_creator.create_all_ttls()


###########################################################################################################
# ttls-to-neo4j
###########################################################################################################


@main.command(
    help=(
        "Create a zipped file with RDF triples (turtle files).\n"
        "\nExample:\n\nbiokb_chebi ttls-to-neo4j -p neo4j_password -d"
    )
)
@click.option(
    "-u",
    "--user",
    default="neo4j",
    show_default=True,
    help="Neo4J user.",
)
@click.option(
    "-p",
    "--password",
    help="Neo4J password.",
)
@click.option(
    "-u",
    "--uri",
    default="neo4j://localhost:7687",
    show_default=True,
    help="Neo4J URI.",
)
@click.option(
    "-f",
    "--path_or_url",
    default=ZIPPED_TTLS_PATH,
    show_default=True,
    help="[Optional] Path to zipped file with turtle files.",
)
@click.option(
    "-d",
    "--delete_existing_graph",
    is_flag=True,
    default=False,
    help="If not set. Nodes and edge will be added to the existing graph.",
)
@click.option(
    "-s",
    "--silent",
    is_flag=True,
    default=False,
    help="If been set, execute silent.",
)
def ttls_to_neo4j(
    user: str,
    password: str,
    uri: str,
    delete_existing_graph: bool,
    path_or_url: str,
    silent: bool,
) -> None:
    """Import the zipped file with ttl into Neo4j

    Args:
        user (str): Neo4j user
        password (str): Neo4j password
        uri (str): Neo4j URI
        delete_existing_graph (bool): If True delete the old ChEBI graph before importing
        path_or_url (str): Local path or URL to zipped file with ttls
        silent (bool): If True silent, no output
    """
    if not silent:
        logging.basicConfig(level=logging.INFO)

    neo4j_importer = Neo4jImporter(
        neo4j_pwd=password,
        neo4j_user=user,
        neo4j_uri=uri,
        delete_existing_graph=delete_existing_graph,
        path_or_url=path_or_url,
    )
    neo4j_importer.import_ttls()
    found_server_name = re.search(r".*?//([^:]+):.*", uri)
    if found_server_name:
        server_name = found_server_name.group(1)
        click.echo(f"Open Neo4J Browser http://{server_name}:7474")


###########################################################################################################
# complete_import
###########################################################################################################


@main.command(
    help=(
        "Easiest way to import all at once (database and Neo4J)\n"
        "\nExample:\n\nbiokb_chebi complete-import -np neo4j_password -mp biokb_chebi_password -mo 3307"
    )
)
@click.option(
    "-mu",
    "--mysql_user",
    default="biokb_chebi_user",
    show_default=True,
    help="MySQL user.",
)
@click.option(
    "-mp",
    "--mysql_password",
    help="MySQL password.",
)
@click.option(
    "-mh",
    "--mysql_host",
    default="localhost",
    show_default=True,
    help="MySQL host.",
)
@click.option(
    "-mo",
    "--mysql_port",
    default=3306,
    show_default=True,
    help="MySQL port.",
    type=int,
)
@click.option(
    "-md",
    "--mysql_database",
    default="biokb_chebi",
    show_default=True,
    help="MySQL port.",
)
@click.option(
    "-nu",
    "--neo4j_user",
    default="neo4j",
    show_default=True,
    help="Neo4J user.",
)
@click.option(
    "-np",
    "--neo4j_password",
    help="Neo4J password.",
)
@click.option(
    "-nu",
    "--neo4j_uri",
    default="neo4j://localhost:7687",
    show_default=True,
    help="Neo4J URI.",
)
@click.option(
    "-nd",
    "--delete_existing_graph",
    is_flag=True,
    default=False,
    help="If not set. Nodes and edge will be added to the existing graph.",
)
@click.option(
    "-udc",
    "--use_default_config",
    is_flag=True,
    default=False,
    help="If been set, use the default config in ~/.biokb/chebi/config.ini.",
)
@click.option(
    "-s",
    "--silent",
    is_flag=True,
    default=False,
    help="If been set, execute silent.",
)
def complete_import(
    mysql_user: str,
    mysql_password: str,
    mysql_host: str,
    mysql_port: int,
    mysql_database: str,
    neo4j_user: str,
    neo4j_password: str,
    neo4j_uri: str,
    data_folder: str,
    delete_existing_graph: bool,
    config_file: str,
    silent: bool,
) -> None:
    """Imports the ChEBI data in the database, writes the zipped file with ttls and imports the triples in Neo4j

    Args:
        mysql_user (_type_): MySQL user
        mysql_password (_type_): MySQL password
        mysql_host (_type_): MySQL host
        mysql_port (_type_): MySQL port
        mysql_database (_type_): MySQL database
        neo4j_user (_type_): Neo4j user
        neo4j_password (_type_): Neo4j password
        neo4j_uri (_type_): Neo4j URI
        delete_existing_graph (_type_): If True delete the old ChEBI graph before importing
        silent (_type_): If True silent, no output
    """
    if not silent:
        logging.basicConfig(level=logging.INFO)

    import_all(
        neo4j_pwd=neo4j_password,
        mysql_password=mysql_password,
        mysql_user=mysql_user,
        mysql_host=mysql_host,
        mysql_port=mysql_port,
        mysql_database=mysql_database,
        neo4j_user=neo4j_user,
        neo4j_uri=neo4j_uri,
        data_folder=data_folder,
        config_file=config_file,
        delete_existing_graph=delete_existing_graph,
    )
