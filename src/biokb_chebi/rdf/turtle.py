"""Module to create RDF turtle files from the ChEBI imported data."""

import logging
import os.path
import re
import shutil
from collections.abc import Callable
from typing import Optional

import pandas as pd
from rdflib import RDF, XSD, Graph, Literal, URIRef
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from biokb_chebi.constants import (
    BASIC_NODE_LABEL,
    DB_DEFAULT_CONNECTION_STR,
    EXPORT_FOLDER,
)
from biokb_chebi.db import models
from biokb_chebi.rdf import namespaces as ns

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger: logging.Logger = logging.getLogger(__name__)


def get_empty_graph() -> Graph:
    """Return an empty RDFlib.Graph with all needed namespaces"""
    graph = Graph()
    graph.bind("c", ns.CHEBI_NS)
    graph.bind("n", ns.NODE_NS)
    graph.bind("r", ns.REL_NS)
    graph.bind("xs", XSD)
    graph.bind("i", ns.INCHI_NS)
    graph.bind("cn", ns.NAME_NS)
    graph.bind("s", ns.CAS_NS)
    return graph


class TurtleCreator:
    """Turtle creator class."""

    def __init__(
        self,
        engine: Optional[Engine] = None,
    ):
        """Init TurtleCreator

        If engine=None tries to get the settings from config ini file

        If export_to_folder=None takes the default path.

        Args:
            engine (Engine | None, optional): SQLAlchemy class. Defaults to None.
            export_to_folder (str | None, optional): _description_. Defaults to None.
        """
        connection_str = os.getenv("CONNECTION_STR", DB_DEFAULT_CONNECTION_STR)
        self.__engine = engine if engine else create_engine(str(connection_str))
        self.Session = sessionmaker(bind=self.__engine)
        self.__ttls_folder = EXPORT_FOLDER

    def _set_ttls_folder(self, export_to_folder: str) -> None:
        """Sets the export folder path.

        This is mainly for testing purposes.
        """
        self.__ttls_folder = export_to_folder

    def create_ttls(self) -> str:
        """Create all turtle files.

        Returns:
            str: path zipped file with ttls.
        """
        os.makedirs(self.__ttls_folder, exist_ok=True)
        create_methods: list[Callable[[], str | list[str]]] = [
            self.__create_compounds_ttl,
            self.__create_inchis_links_ttl,
            self.__create_names_ttl,
            self.__create_xrefs_ttl,
            self.__create_compound_relations_ttl,
        ]
        for create_method in create_methods:
            create_method()

        return self.__create_zip_from_all_ttls()

    def __create_zip_from_all_ttls(self) -> str:
        """Create a zipped file from all turtle file and return the path.

        Returns:
            str: path to zipped file
        """
        path_to_zip_file = shutil.make_archive(
            base_name=self.__ttls_folder, format="zip", root_dir=self.__ttls_folder
        )
        logger.info(f"Zipped ttls create in {path_to_zip_file}")
        shutil.rmtree(self.__ttls_folder)
        return path_to_zip_file

    def __create_compounds_ttl(self) -> str:
        """Create compound turtle file."""
        ttl_path = os.path.join(self.__ttls_folder, "compound.ttl")
        logger.info("Create compound ttl")
        graph = get_empty_graph()

        with self.Session() as session:
            compounds = session.query(
                models.Compound.id,
                models.Compound.ascii_name,
                models.Compound.source,
                models.Compound.status_id,
                models.Compound.definition,
                models.Compound.stars,
                models.Compound.parent_id,
            ).all()
            for comp in tqdm(compounds):
                compound = ns.CHEBI_NS[str(comp.id)]
                graph.add((compound, RDF.type, ns.NODE_NS["Compound"]))
                graph.add((compound, RDF.type, ns.NODE_NS[BASIC_NODE_LABEL]))

                for column in ["ascii_name", "source", "status_id", "definition"]:
                    if not pd.isna(getattr(comp, column)):
                        graph.add(
                            (
                                compound,
                                ns.REL_NS[column],
                                Literal(getattr(comp, column), datatype=XSD.string),
                            )
                        )
                graph.add(
                    (
                        compound,
                        ns.REL_NS["star"],
                        Literal(int(comp.stars), datatype=XSD.integer),
                    )
                )
                if comp.parent_id:
                    parent = ns.CHEBI_NS[str(comp.parent_id)]
                    graph.add((compound, ns.REL_NS["HAS_PARENT"], parent))

        graph.serialize(ttl_path, format="turtle")
        return ttl_path

    def __create_inchis_links_ttl(self) -> str:
        """Create Compound/InChi links turtle file."""
        ttl_path = os.path.join(self.__ttls_folder, "inchi.ttl")
        logger.info("Create InChi ttl")
        graph = get_empty_graph()

        with self.Session() as session:
            inchis: list[models.Structure] = (
                session.query(models.Structure)
                .where(models.Structure.standard_inchi_key.isnot(None))
                .all()
            )

            for inc in tqdm(inchis):
                inchi = ns.INCHI_NS[str(inc.standard_inchi_key)]
                graph.add((inchi, RDF.type, ns.NODE_NS["InChI"]))
                compound = URIRef(ns.CHEBI_NS[str(inc.compound_id)])
                graph.add((compound, ns.REL_NS["SAME_AS"], inchi))

        graph.serialize(ttl_path, format="turtle")
        del graph
        return ttl_path

    def __create_names_ttl(self) -> str:
        """Create ChEBI name turtle file.

        Returns:
            str: Path to create turtle file.
        """
        ttl_path = os.path.join(self.__ttls_folder, "name.ttl")
        logger.info("Create ChEBI names ttl")
        graph = get_empty_graph()

        with self.Session() as session:
            names = (
                session.query(models.Name)
                .where(models.Name.ascii_name.isnot(None))
                .all()
            )

            for name in tqdm(names):
                node_label = "Name" + name.type.capitalize().replace(" ", "")
                chebi_name = ns.NAME_NS[str(name.id)]
                graph.add((chebi_name, RDF.type, ns.NODE_NS[node_label]))
                graph.add((chebi_name, RDF.type, ns.NODE_NS["OtherName"]))
                graph.add((chebi_name, RDF.type, ns.NODE_NS[BASIC_NODE_LABEL]))
                compound = URIRef(ns.CHEBI_NS[str(name.compound_id)])
                graph.add((compound, ns.REL_NS["HAS_NAME"], chebi_name))

                for column in ["adapted", "language_code", "ascii_name", "status_id"]:
                    value = getattr(name, column)
                    datatype = XSD.string if isinstance(value, str) else XSD.integer
                    graph.add(
                        (
                            chebi_name,
                            ns.REL_NS[column],
                            Literal(value, datatype=datatype),
                        )
                    )
        graph.serialize(ttl_path, format="turtle")
        del graph
        return ttl_path

    def __create_xrefs_ttl(
        self,
        include: list[str] = [
            "gxa.expt",
            "gxa.expt",
            "biomodels.db",
            "bindingdb",
            "reactome",
            "chembl",
            "surechembl",
            "brenda.ligand",
            "go",
            "rhea",
            "eccode",
        ],
        exclude: list[str] = [],
    ) -> list[str]:
        """Create xref turtle file.

        Returns:
            str: Path to turtle file with xref links.
        """
        with self.Session() as session:
            sources: list[models.Source] = session.query(models.Source).all()
            if include:
                sources = [source for source in sources if source.prefix in include]
            if exclude:
                sources = [source for source in sources if source.prefix not in exclude]

            references = (
                session.query(models.Reference)
                .where(models.Reference.source_id.in_([x.id for x in sources]))
                .all()
            )
            ttl_paths: list[str] = []
            for source in sources:
                if source.prefix not in ns.REF_NS_DICT:
                    logger.warning(
                        f"Source prefix {source.prefix} not in REF_NS_DICT. Skipping."
                    )
                    continue
                ttl_path = os.path.join(
                    self.__ttls_folder,
                    f"{source.prefix.replace('.', '_').lower()}_xref.ttl",
                )
                logger.info(f"Create {source.name} xref ttl")

                graph = get_empty_graph()
                graph.bind("e", ns.REF_NS_DICT[source.prefix])

                references = (
                    session.query(models.Reference)
                    .filter(models.Reference.source_id == source.id)
                    .all()
                )
                for ref in tqdm(references, desc=f"Creating xrefs for {source.prefix}"):
                    compound = URIRef(ns.CHEBI_NS[str(ref.compound_id)])
                    xref = ns.REF_NS_DICT[source.prefix][str(ref.accession_number)]
                    node_label = "Xref" + re.sub(r"\W", "", source.prefix.capitalize())
                    graph.add((xref, RDF.type, ns.NODE_NS[node_label]))
                    graph.add((compound, ns.REL_NS["HAS_XREF"], xref))
                ttl_paths.append(ttl_path)
                if len(graph):
                    graph.serialize(ttl_path, format="turtle")
                del graph
            return ttl_paths

    def __create_compound_relations_ttl(self) -> str:
        """Create compound relation turtle file.

        Returns:
            str: Path to turtle file with ChEBI relations.
        """
        ttl_path = os.path.join(self.__ttls_folder, "relation.ttl")
        logger.info("Create ChEBI compound relations ttl")
        graph = get_empty_graph()

        with self.Session() as session:
            relations = session.query(models.Relation).all()
            for rel in tqdm(relations):
                compound_1 = URIRef(ns.CHEBI_NS[str(rel.init_id)])
                compound_2 = URIRef(ns.CHEBI_NS[str(rel.final_id)])
                if rel.relation_type:
                    graph.add(
                        (
                            compound_1,
                            ns.REL_NS[str(rel.relation_type.code).upper()],
                            compound_2,
                        )
                    )

        graph.serialize(ttl_path, format="turtle")
        del graph
        return ttl_path


def create_ttls(
    engine: Optional[Engine] = None,
    export_to_folder: Optional[str] = None,
) -> str:
    """Create all turtle files.

    If engine=None tries to get the settings from config ini file

    If export_to_folder=None takes the default path.

    Args:
        engine (Engine | None, optional): SQLAlchemy class. Defaults to None.
        export_to_folder (str | None, optional): Folder to export ttl files.
            Defaults to None.

    Returns:
        str: path zipped file with ttls.
    """
    ttl_creator = TurtleCreator(engine=engine)
    if export_to_folder:
        ttl_creator._set_ttls_folder(export_to_folder)
    return ttl_creator.create_ttls()
