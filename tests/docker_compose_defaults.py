"""Constants used in ../docker-compose.yaml and ../docker-compose-test.yaml"""

# default MySQL server
MYSQL_USER = "biokb_chebi_user"
MYSQL_PASSWORD = "biokb_chebi_password"
MYSQL_DATABASE = "biokb_chebi"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3307

# test MySQL server
MYSQL_USER_TEST = "biokb_chebi_user"
MYSQL_PASSWORD_TEST = "biokb_chebi_password"
MYSQL_DATABASE_TEST = "biokb_chebi"
MYSQL_HOST_TEST = "127.0.0.1"
MYSQL_PORT_TEST = 3308

# default Neo4J server
NEO4J_PASSWD = "neo4j_password"
NEO4J_USER = "neo4j"
NEO4J_URI = "neo4j://localhost:7688"

# test Neo4J server
NEO4J_PASSWD_TEST = "neo4j_password"
NEO4J_USER_TEST = "neo4j"
NEO4J_URI_TEST = "neo4j://localhost:7689"
