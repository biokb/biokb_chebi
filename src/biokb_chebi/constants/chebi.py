"""Chebi constants."""

FTP_SERVER = "ftp.ebi.ac.uk"
FTP_DIR = "/pub/databases/chebi/Flat_file_tab_delimited/"

# files on ftp server in FTP_DIR
CHEMICAL_DATA_FILE = "chemical_data.tsv"
COMMENT_FILE = "comments.tsv"
COMPOUND_FILE = "compounds.tsv.gz"
DATABASE_ACCESSION_FILE = "database_accession.tsv"
NAME_FILE = "names.tsv.gz"
REFERENCE_FILE = "reference.tsv.gz"
RELATION_FILE = "relation.tsv"
STRUCTURE_FILE = "structures.csv.gz"
INCHI_FILE = "chebiId_inchi.tsv"

CHEBI_URI = "http://purl.obolibrary.org/obo/CHEBI_"
BIOKB_URI = "https://biokb.scai.fraunhofer.de"
BASE_URI = f"{BIOKB_URI}/chebi"

BASIC_NODE_LABEL = "DbChEBI"
