"""RDF namespace URIs."""

from rdflib import Namespace

from biokb_chebi.constants import BASE_URI, BIOKB_URI, CHEBI_URI

# ChEBI URIs to Fraunhofer
CHEBI_NS = Namespace(CHEBI_URI)
NODE_NS = Namespace(f"{BASE_URI}/node#")
REL_NS = Namespace(f"{BASE_URI}/relation#")
NAME_NS = Namespace(f"{BASE_URI}/name#")
CAS_NS = Namespace(f"{BASE_URI}/cas#")
RDF_NS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
PATENT_NS = Namespace(f"{BIOKB_URI}/patent#")
INCHI_NS = Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/inchikey/")
UNIPROT_NS = Namespace("http://purl.uniprot.org/uniprot/")
GO_NS = Namespace("http://purl.obolibrary.org/obo/GO_")

REF_NS_DICT: dict[str, Namespace] = {
    "biomodels.db": Namespace(
        "https://www.ebi.ac.uk/biomodels/"
    ),  # db quantitative kinetic models of biochemical and cellular systems
    "carotenoids_database": Namespace(
        "http://carotenoiddb.jp/Entries/"
    ),  # db of carotenoids
    "chembl": Namespace(
        "https://www.ebi.ac.uk/chembl/id_lookup/"
    ),  # db of bioactive drug-like small molecules
    "comptox": Namespace(
        "https://comptox.epa.gov/dashboard/chemical/details/"
    ),  # db of environmental chemicals
    "eccode": Namespace(
        "https://www.brenda-enzymes.org/enzyme.php?ecno="
    ),  # db of enzyme nomenclature
    # Gene Ontology
    "go": Namespace("https://amigo.geneontology.org/amigo/term/"),
    "gxa.expt": Namespace(
        "https://www.ebi.ac.uk/gxa/experiments/"
    ),  # Gene Expression Atlas experiments
    "intact": Namespace(
        "https://www.ebi.ac.uk/intact/details/interaction/"
    ),  # molecular interaction database
    "metabolights": Namespace(
        "https://www.ebi.ac.uk/metabolights/editor/"
    ),  # db for metabolomics experiments and derived information
    "nmrshiftdb2": Namespace(
        "https://nmrshiftdb.nmr.uni-koeln.de/portal/js_pane/P-Results/"
        "nmrshiftdbaction/showDetailsFromHome/molNumber/"
    ),  # db for organic structures and their NMR data
    "patent": Namespace(
        "https://worldwide.espacenet.com/patent/search?q="
    ),  # patent database
    "pdb": Namespace(
        "https://identifiers.org/pdb:"
    ),  # Protein Data Bank, 3d structures of proteins and nucleic acids
    "pubchem.compound": Namespace(
        "https://pubchem.ncbi.nlm.nih.gov/compound/"
    ),  # db of chemical molecules and their activities
    "pubchem.substance": Namespace(
        "https://pubchem.ncbi.nlm.nih.gov/substance/"
    ),  # db of chemical substances
    "reactome": Namespace(
        "https://reactome.org/content/detail/"
    ),  # db of biological pathways
    "rhea": Namespace("https://www.rhea-db.org/rhea/"),  # db of biochemical reactions
    "sabiork.reaction": Namespace(
        "https://sabiork.h-its.org/reacdetails.jsp?reactid="
    ),  # db of kinetic data of biochemical reactions
    "slm": Namespace("https://www.swisslipids.org/#/entity/"),  # db of lipid structures
    "spp": Namespace(
        "http://www.signalingpathways.org/datasets/dataset.jsf?doi="
    ),  # signaling pathways database
    "surechembl": Namespace(
        "https://www.surechembl.org/chemical/"
    ),  # db of compounds with bioactivity data
    "uniprot": Namespace(
        "http://www.uniprot.org/entry/*"
    ),  # universal protein resource
    "virtual_metabolic_human": Namespace(
        "https://www.vmh.life/#metabolite/"
    ),  # db of human metabolism
    "brenda.ligand": Namespace(
        "https://www.brenda-enzymes.de/ligand.php?brenda_ligand_id="
    ),  # db of enzyme ligands
    "bindingdb": Namespace(
        "http://www.bindingdb.org/rwd/entry/"
    ),  # db of measured binding affinities
}
