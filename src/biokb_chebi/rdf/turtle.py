"""Module to create RDF turtle files from the ChEBI imported data."""

import logging
import os.path
import shutil
from tqdm import tqdm
from typing import Optional

import pandas as pd
from biokb_chebi.constants.basic import EXPORT_FOLDER
from biokb_chebi.constants.chebi import BASIC_NODE_LABEL
from biokb_chebi.rdf import namespaces as ns
from pandas import DataFrame
from rdflib import RDF, XSD, Graph, Literal, URIRef
from rdkit.Chem.inchi import InchiToInchiKey
from sqlalchemy import Engine

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger: logging.Logger = logging.getLogger(__name__)


def get_empty_graph() -> Graph:
    """Return an empty RDFlib.Graph with all needed namespaces"""
    graph = Graph()
    graph.bind("chebi", ns.chebi)
    graph.bind("node", ns.node)
    graph.bind("relation", ns.relation)
    graph.bind("xs", XSD)
    graph.bind("inchi", ns.inchi)
    graph.bind("chebi_name", ns.name)
    graph.bind("cas", ns.cas)
    graph.bind("patent", ns.patent)
    return graph


class TurtleCreator:
    """Turtle creator class."""

    def __init__(
        self,
        engine: Engine,
        export_to_folder: Optional[str] = None,
    ):
        """Init TurtleCreator

        If engine=None tries to get the settings from config ini file

        If export_to_folder=None takes the default path.

        Args:
            engine (Engine | None, optional): SQLAlchemy class. Defaults to None.
            export_to_folder (str | None, optional): _description_. Defaults to None.
        """
        self.engine = engine
        if export_to_folder:
            ttls_folder = os.path.join(export_to_folder, "ttls")
            self.__ttls_folder = ttls_folder
        else:
            self.__ttls_folder = EXPORT_FOLDER
        if not os.path.exists(self.__ttls_folder):
            os.makedirs(self.__ttls_folder)

    def create_all_ttls(self) -> str:
        """Create all turle files.

        Returns:
            str: path zipped file with ttls.
        """
        create_methods = [
            self.create_compounds_ttl,
            self.create_inchis_ttl,
            self.create_names_ttl,
            self.create_cas_numbers_ttl,
            self.create_patents_ttl,
            self.create_compound_relations_ttl,
        ]
        for create_method in tqdm(create_methods, desc="Create turtle files"):
            create_method()

        return self.create_zip_from_all_ttls()

    def create_zip_from_all_ttls(self) -> str:
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

    @property
    def compound_df(self) -> DataFrame:
        """Return ChEBI compound dataframe for status C and E

        1. C = Checked and published by ChEBI curators.
        2. E = Exists but not been checked by one of our curators.

        """
        sql = (
            "SELECT id, name, source, status, star, definition "
            "FROM chebi_compound WHERE status in ('C', 'E') AND parent_id IS NULL"
        )
        return pd.read_sql(sql, self.engine)

    def create_compounds_ttl(self) -> None:
        """Create compound turtle file."""
        ttl_path = os.path.join(self.__ttls_folder, "compound.ttl")
        logger.info(f"Create compound ttl and save in {ttl_path}")
        graph = get_empty_graph()

        for i, row in self.compound_df.iterrows():
            subject = ns.chebi[str(row.id)]
            graph.add((subject, RDF.type, ns.node["Compound"]))
            graph.add((subject, RDF.type, ns.node[BASIC_NODE_LABEL]))

            for column in ["name", "source", "status", "definition"]:
                if not pd.isna(row[column]):
                    graph.add(
                        (
                            subject,
                            ns.relation[column],
                            Literal(row[column], datatype=XSD.string),
                        )
                    )

        graph.serialize(ttl_path, format="turtle")
        del graph

    @property
    def inchi_df(self) -> DataFrame:
        """Return ChEBI InCHI dataframe."""
        sql = (
            "SELECT i.compound_id, i.inchi FROM chebi_inchi i INNER JOIN "
            "chebi_compound c ON (c.id=i.compound_id) "
            "WHERE c.status in ('C', 'E') AND c.parent_id IS NULL"
        )
        df: DataFrame = pd.read_sql(sql, self.engine)
        df["inchikey"] = df.inchi.apply(lambda x: InchiToInchiKey(x))
        return df

    def create_inchis_ttl(self) -> None:
        """Create InChi turtle file."""
        ttl_path = os.path.join(self.__ttls_folder, "inchi.ttl")
        logger.info(f"Create InChi ttl and save in {ttl_path}")
        graph = get_empty_graph()

        for i, row in self.inchi_df.iterrows():
            inchi = ns.inchi[str(row.inchikey)]
            graph.add((inchi, RDF.type, ns.node["InChI"]))
            graph.add((inchi, RDF.type, ns.node[BASIC_NODE_LABEL]))
            compound = URIRef(ns.chebi[str(row.compound_id)])
            graph.add((compound, ns.relation["HAS_INCHI"], inchi))

            for column in ["inchi", "inchikey"]:
                if not pd.isna(row[column]):
                    graph.add(
                        (
                            inchi,
                            ns.relation[column],
                            Literal(row[column], datatype=XSD.string),
                        )
                    )

        graph.serialize(ttl_path, format="turtle")
        del graph

    @property
    def name_df(self) -> DataFrame:
        """Return ChEBI InCHI dataframe.

        Returns:
            DataFrame: DataFrame with ChEBI names
        """
        sql = (
            "SELECT n.id,n.name, n.type, n.source, n.adapted, n.language,n.compound_id "
            "FROM chebi_name n INNER JOIN chebi_compound c ON (c.id=n.compound_id) "
            "WHERE c.status in ('C', 'E') AND c.parent_id IS NULL"
        )
        df: DataFrame = pd.read_sql(sql, self.engine)
        return df

    def create_names_ttl(self) -> str:
        """Create ChEBI name turtle file.

        Returns:
            str: Path to create turtle file.
        """
        ttl_path = os.path.join(self.__ttls_folder, "name.ttl")
        logger.info(f"Create ChEBI names ttl and save in {ttl_path}.")
        graph = get_empty_graph()

        for i, row in self.name_df.iterrows():
            chebi_name = ns.name[str(row.id)]
            graph.add((chebi_name, RDF.type, ns.node["Name"]))
            graph.add((chebi_name, RDF.type, ns.node[BASIC_NODE_LABEL]))
            compound = URIRef(ns.chebi[str(row.compound_id)])
            graph.add((compound, ns.relation["HAS_NAME"], chebi_name))

            for column in ["type", "source", "adapted", "language", "name"]:
                if not pd.isna(row[column]):
                    graph.add(
                        (
                            chebi_name,
                            ns.relation[column],
                            Literal(row[column], datatype=XSD.string),
                        )
                    )
        graph.serialize(ttl_path, format="turtle")
        del graph
        return ttl_path

    @property
    def cas_number_df(self) -> DataFrame:
        """Return CAS number dataframe."""
        sql = """SELECT 
            da.accession_number as number, 
            group_concat(distinct da.source order by da.source) as sources, 
            da.compound_id  
        FROM  
            chebi_database_accession da INNER JOIN 
            chebi_compound c ON (c.id=da.compound_id)
        WHERE 
            da.type='CAS Registry Number' AND c.status in ('C', 'E') AND 
            c.parent_id IS NULL 
        GROUP BY 
            da.compound_id, da.accession_number"""
        return pd.read_sql(sql, self.engine)

    def create_cas_numbers_ttl(self) -> str:
        """Create CAS number turtle file.

        Returns:
            str: Path to turtle file with CAS numbers.
        """
        ttl_path = os.path.join(self.__ttls_folder, "cas.ttl")
        logger.info(f"Create CAS number ttl and save in {ttl_path}")
        graph = get_empty_graph()

        for i, row in self.cas_number_df.iterrows():
            cas = ns.cas[str(row.number)]
            graph.add((cas, RDF.type, ns.node["Cas"]))
            graph.add((cas, RDF.type, ns.node[BASIC_NODE_LABEL]))
            compound = URIRef(ns.chebi[str(row.compound_id)])
            graph.add((compound, ns.relation["HAS_CAS"], cas))

            for column in ["number", "sources"]:
                if not pd.isna(row[column]):
                    graph.add(
                        (
                            cas,
                            ns.relation[column],
                            Literal(row[column], datatype=XSD.string),
                        )
                    )
        graph.serialize(ttl_path, format="turtle")
        del graph
        return ttl_path

    @property
    def patent_df(self) -> DataFrame:
        """Return patent dataframe."""
        sql = (
            "SELECT r.reference_id as patent_id, r.reference_name name, r.compound_id "
            "FROM  `chebi_reference` r INNER JOIN chebi_compound c ON (c.id=r.compound_id) "
            "WHERE `reference_db_name` = 'Patent' AND c.status in ('C', 'E') AND c.parent_id IS NULL"
        )
        return pd.read_sql(sql, self.engine)

    def create_patents_ttl(self) -> str:
        """Create patent turtle file.

        Returns:
            str: Path to turtle file with patents.
        """
        ttl_path = os.path.join(self.__ttls_folder, "patent.ttl")
        logger.info(f"Create patent ttl and save in {ttl_path}")
        graph = get_empty_graph()

        for i, row in self.patent_df.iterrows():
            patent = ns.cas[str(row.patent_id)]
            graph.add((patent, RDF.type, ns.node["Patent"]))
            graph.add((patent, RDF.type, ns.node[BASIC_NODE_LABEL]))
            compound = URIRef(ns.chebi[str(row.compound_id)])
            graph.add((compound, ns.relation["HAS_PATENT"], patent))

            for column in ["name", "patent_id"]:
                if not pd.isna(row[column]):
                    graph.add(
                        (
                            patent,
                            ns.relation[column],
                            Literal(row[column], datatype=XSD.string),
                        )
                    )
        graph.serialize(ttl_path, format="turtle")
        del graph
        return ttl_path

    @property
    def chebi_compound_relation_df(self) -> DataFrame:
        """Return ChEBI compound relation dataframe."""
        sql = (
            "SELECT r.type, init_id, final_id FROM chebi_relation r "
            "inner join chebi_compound c1 ON (c1.id=r.init_id) "
            "inner join chebi_compound c2 ON (c2.id=r.final_id) "
            "WHERE r.status in ('C','E') and "
            "c1.status in ('C', 'E') and c2.status in ('C', 'E')"
        )
        return pd.read_sql(sql, self.engine)

    def create_compound_relations_ttl(self) -> str:
        """Create compound relation turtle file.

        Returns:
            str: Path to turle file with ChEBI relations.
        """
        ttl_path = os.path.join(self.__ttls_folder, "relation.ttl")
        logger.info(f"Create ChEBI compound relations ttl and save in {ttl_path}")
        graph = get_empty_graph()

        for i, row in self.chebi_compound_relation_df.iterrows():
            compound_1 = URIRef(ns.chebi[str(row.init_id)])
            compound_2 = URIRef(ns.chebi[str(row.final_id)])
            graph.add((compound_2, ns.relation[str(row.type).upper()], compound_1))

        graph.serialize(ttl_path, format="turtle")
        del graph
        return ttl_path
