![docs/imgs/](https://raw.githubusercontent.com/biokb/biokb_chebi/refs/heads/main/docs/imgs/biokb_logo_writing.png)
# BioKb-ChEBI

![](https://img.shields.io/pypi/v/biokb_chebi?color=blue&label=biokb_chebi&style=flat-square)
![](https://img.shields.io/pypi/pyversions/biokb_chebi?style=flat-square)
![](https://img.shields.io/pypi/l/biokb_chebi?style=flat-square)



BioKb-ChEBI (biokb_chebi) is a python package to import ChEBI data into a relational database and create RDF triples (turtles) from it. The turtles can be imported into a Neo4J graph database. The package is part of the [BioKb family of packages](https://github.com/biokb) to create and connect biological and medical knowledge bases and graphs.

![Components](https://raw.githubusercontent.com/biokb/biokb_chebi/refs/heads/main/docs/imgs/components.png)

The package provides different options to run it: from command line, as RESTful API server, as Podman/Docker container, or as Podman/Docker networked containers with Neo4J and a relational database.

## Features

biokb_chebi allows to ...

1. Query ChEBI data with SQLAlchemy or raw SQL
2. Load, query and manage ChEBI data with GUIs for knowledge base and graphs (phpMyAdmin, Neo4J Browser)
3. Query data via a RESTful API (FastAPI) with OpenAPI documentation and interactive Swagger-UI

to provide this ***biokb_chebi*** ...

- imports [ChEBI](https://www.ebi.ac.uk/chebi/) data into a relational database 
- creates [RDF](https://www.w3.org/RDF/) triples (turtles) from the relational database
- imports the RDF triples into a [Neo4J](https://neo4j.com) graph database

***Supported databases***: [SQLite](https://sqlite.org/), [MariaDB](https://go.mariadb.com)/[MySQL](https://www.mysql.com/), [PostgreSQL](https://www.postgresql.org/), [Oracle](https://www.oracle.com/database/), [Microsoft SQL Server](https://www.microsoft.com/en-us/sql-server), and any other database [supported by SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/engines.html#supported-databases).


### Options to run BioKb-ChEBI

All biokb packages share the same API and CLI structure. You have different options to run the packages:

1. [from command line](#from-command-line) (simplest way to get started)
2. [as RESTful API server](#as-restful-api-server) (can start directly from command line)
3. [as Podman/Docker container](#as-podmandocker-container) (without import into Neo4J, but export of turtles possible)
4. [as Podman/Docker networked containers](#as-podmandocker-networked-containers) (with all features) and 3 containers: 
   1. high-performance relational databases (PostgreSQL, Oracle, MySQL, ...)
   2. RESTful API (fastAPI) for queries, data import and export
   3. GUI for querying and administration of MySQL over the Web