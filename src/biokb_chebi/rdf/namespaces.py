"""RDF namespace URIs."""

from rdflib import Namespace
from biokb_chebi.constants.chebi import BASE_URI, BIOKB_URI, CHEBI_URI

# ChEBI URIs to Fraunhofer
chebi = Namespace(CHEBI_URI)
node = Namespace(f"{BASE_URI}/node#")
relation = Namespace(f"{BASE_URI}/relation#")
name = Namespace(f"{BASE_URI}/name#")
cas = Namespace(f"{BASE_URI}/cas#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
patent = Namespace(f"{BIOKB_URI}/patent#")
inchi = Namespace(f"{BIOKB_URI}/chemistry/inchi#")
uniprot = Namespace("http://purl.uniprot.org/uniprot/")
