![docs/imgs/](https://raw.githubusercontent.com/biokb/biokb_chebi/refs/heads/main/docs/imgs/biokb_logo_writing.png)

# BioKb-ChEBI

![](https://img.shields.io/pypi/v/biokb-chebi?style=flat-square)
![](https://img.shields.io/pypi/pyversions/biokb-chebi?style=flat-square)
![](https://img.shields.io/github/actions/workflow/status/biokb/biokb_chebi/pypi-publish.yml?style=flat-square)
![](https://img.shields.io/github/license/biokb/biokb_chebi?style=flat-square)

BioKb-ChEBI (biokb_chebi) is a python package to import [ChEBI (Chemical Entities of Biological Interest)](https://www.ebi.ac.uk/chebi/) data into a relational database and create RDF triples (turtles) from it. The turtle files can be imported into a [Neo4J graph database](https://neo4j.com/product/neo4j-graph-database/) or any other RDF-compatible graph database like [Fuseki](https://jena.apache.org/documentation/fuseki2/). The package is part of the [BioKb family of packages](https://github.com/biokb) to create and connect biological and medical knowledge bases and graphs.

![Components](https://raw.githubusercontent.com/biokb/biokb_chebi/refs/heads/main/docs/imgs/components.png)

***Fig. 1***: *Components of BioKb-ChEBI: Data are imported from ChEBI into a relational database, transformed into RDF triples, and then imported into a graph database. A Restful API provides access to the data and facilitates queries and data management.*

`biokb_chebi` provides different options to run it:

1. command line (`biokb_chebi import-data`, `biokb_chebi create-ttls` and `biokb_chebi import-neo4j`)
2. RESTful API server ([FastAPI](https://fastapi.tiangolo.com/))
3. [Podman](https://podman.io/)/Docker container
4. Podman/Docker networked containers with phpMyAdmin, Neo4J and MySQL (using [`podman-compose`](https://github.com/containers/podman-compose) or [`docker-compose`](https://github.com/docker/compose)).

## Quick Start

All further instructions assume that `uv` (and [GitBash on Windows](https://git-scm.com/install/windows)) are installed. . Go [here](#uv-installationupgrade) for instructions on installing or upgrading `uv`.

### Setup Virtual Environment

create a test folder and navigate into it:

```bash
mkdir test_folder
cd test_folder
```

create a virtual environment using `uv`:

**Linux / macOS**:

```bash
# create and activate virtual environment using uv
uv venv
source .venv/bin/activate
```

**Windows (Git Bash)**:

```bash
# create and activate virtual environment using uv
uv venv
source .venv\Scripts\activate
```

### Install `biokb_chebi`

You have 2 options to install `biokb_chebi` using `uv pip install`:

**Option 1: Install the latest version from PyPI**

```bash
uv pip install biokb_chebi
```

**Option 2: Install the latest development version from GitHub**

```bash
uv pip install git+https://github.com/biokb/biokb_chebi.git
```

Option 2 is recommended if you want to use the latest version with the most recent updates and features.

### Import imported data

In the terminal (cli commands):

```bash
biokb_chebi import-data
```

Output will show some information about the data import and database location/connection:

```bash
biokb_chebi.tools - INFO - No environment file provided or CONNECTION_STR not found. Using default connection string sqlite:////path/to/your/home/.biokb/biokb.db.
biokb_chebi.db.manager - INFO - Engine: Engine(sqlite:////path/to/your/home/.biokb/biokb.db)
biokb_chebi.db.manager - INFO - Data folder: /path/to/your/home/.biokb/chebi/data
biokb_chebi.db.manager - INFO - Start download of data
100%|███████████████████████████████████████████████████████████████████████████████████| 11/11 [00:00<00:00, 121414.06it/s]
biokb_chebi.db.manager - INFO - Files already exist: 11
biokb_chebi.db.manager - INFO - Files downloaded: 0
biokb_chebi.db.manager - INFO - Insert data in database
100%|███████████████████████████████████████████████████████████████████████████████████| 11/11 [02:18<00:00, 12.57s/it]
```

As Python functions in a script:

```python
from biokb_chebi import import_data, create_ttls
import_data()
create_ttls()
```

If you want to test the import into a Neo4j database, start a temporary container wiith podman:

```bash
podman run --rm --name biokb-neo4j-test -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/neo4j_password neo4j:latest
```

and then in the terminal (still in the same virtual enviroment) ...

```bash
biokb_chebi import-neo4j
```

Type in your password (neo4j_password), and open http://localhost:7474 for checking the import.

## Features

`biokb_chebi` allows to ...

1. Query ChEBI data with SQLAlchemy or raw SQL -> see examples in the [Relational Database Jupyter Notebook](notebooks/relational_database.ipynb)
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

## Installation

If [uv](https://docs.astral.sh/uv/) is installed:

```bash
uv venv
source .venv/bin/activate
uv pip install biokb_chebi
```

Otherwise:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install biokb_chebi
```

## Run BioKb-ChEBI

### From command line

For sure the simplest way is to run all steps:

```bash
biokb_chebi import-data
biokb_chebi create-ttls
```

Before importing into Neo4J, make sure Neo4J is running (see below "[How to run Neo4J](#how-to-run-neo4j)").

Then import into Neo4J:

```bash
biokb_chebi import-neo4j -p neo4j_password
```

http://localhost:7474  (user/password: neo4j/neo4j_password)

For more options see the [CLI options](#cli-options) section below.

### As RESTful API server

***Usage:*** `biokb_chebi run-server [OPTIONS]`

```bash
biokb_chebi run-server
```

- ***user***: admin
- ***password***: admin

| Option | long       | Description     | default |
| ------ | ---------- | --------------- | ------- |
| -P     | --port     | API server port | 8000    |
| -u     | --user     | API username    | admin   |
| -p     | --password | API password    | admin   |

http://localhost:8000/docs#/

1. [Import data](<http://localhost:8000/docs#/Database%20Management/import_data_import_data__post>)
2. [Export ttls](<http://localhost:8000/docs#/Database%20Management/get_report_export_ttls__get>)
3. Run Neo4J (see below "[How to run Neo4J](#how-to-run-neo4j)")
4. [Import Neo4J](<http://localhost:8000/docs#/Database%20Management/import_neo4j_import_neo4j__get>)

Be patient, each step takes several minutes.

### As Podman/Docker container

For docker just replace `podman` with `docker` in the commands below.

Build & run with Podman:

```bash
git clone https://github.com/biokb/biokb_chebi.git
cd biokb_chebi
podman build -t biokb_chebi_image .
podman run -d --rm --name biokb_chebi_simple -p 8000:8000 biokb_chebi_image
```

- Login: admin
- Password: admin

With environment variable for user and password for more security:

```bash
podman run -d --rm --name biokb_chebi_simple -p 8000:8000 -e API_PASSWORD=your_secure_password -e API_USER=your_secure_user biokb_chebi_image
```

http://localhost:8000/docs

On the website:

1. [Import data](<http://localhost:8000/docs#/Database%20Management/import_data_import_data__post>)
2. [Export ttls](<http://localhost:8000/docs#/Database%20Management/get_report_export_ttls__get>)

Neo4j import in this context is not possible because Neo4J is not running in the same network as service, but the exported turtles can be imported into any Neo4J instance using the CLI (`biokb_chebi import-neo4j`).

to stop the container:

```bash
podman stop biokb_chebi_simple
```

to rerun the container:

```bash
podman start biokb_chebi_simple
```

### Run as Podman/Docker networked containers

If you have docker or podman on your system, the easiest way to run all components (relational database, RESTful API server, phpMyAdmin GUI) is to use networked containers with `podman-compose`/`docker-compose`.

```bash
git clone https://github.com/biokb/biokb_taxtree.git
cd biokb_taxtree
podman-compose -f docker-compose.yml --env-file .env_template up -d
podman-compose --env-file .env_template up -d
```

http://localhost:8001/docs

On the website:

1. [Import data](<http://localhost:8001/docs#/Database%20Management/import_data_import_data__post>)
2. [Export ttls](<http://localhost:8001/docs#/Database%20Management/get_report_export_ttls__get>)
3. [Import Neo4J](<http://localhost:8001/docs#/Database%20Management/import_neo4j_import_neo4j__get>)

stop with:

```bash
podman pod stop pod_biokb_db
podman-compose stop
```

rerun with:

```bash
podman pod start pod_biokb_db
podman-compose start
```

***Tip***: Copy the `.env_template` to `.env` and change the default passwords in the `.env` file before starting the containers for better security. If you have done that you need to use `--env-file .env` instead of `--env-file .env_template` in the commands above or just omit the `--env-file` option (because the default is `.env`).

## CLI Options

### Import data into relational database

***Usage:*** `biokb_chebi import-data [OPTIONS]`

```
biokb_chebi import-data
```

-> SQLite database in `~/.biokb/biokb.db`. Open with e.g. [DB Browser for SQLite](https://sqlitebrowser.org/)

| Option | long                     | Description                               | default            |
| ------ | ------------------------ | ----------------------------------------- | ------------------ |
| -f     | --force-download         | Force re-download of the source file      | False              |
| -k     | --keep-files             | Keep downloaded source files after import | False              |
| -c     | --connection-string TEXT | SQLAlchemy engine URL                     | sqlite:///chebi.db |

If you want to use different relational database (MySQL, PostgreSQL, etc.), provide the connection string with `-c` option. Examples:

- MySQL: `mysql+pymysql://user:password@localhost/biokb`
- PostgreSQL: `postgresql+psycopg2://user:password@localhost/biokb`

For more examples please check [how to create database URLs](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)

### Create RDF turtles

***Usage:*** `biokb_chebi create-ttls [OPTIONS]`

```
biokb_chebi create-ttls
```

-> RDF turtles will be created in `~/.biokb/chebi/data/ttls.zip`

| Option | long                     | Description           | default            |
| ------ | ------------------------ | --------------------- | ------------------ |
| -c     | --connection-string TEXT | SQLAlchemy engine URL | sqlite:///chebi.db |

### Import into Neo4J

Start Neo4J ...

```bash
podman run --rm --name biokb-neo4j-test -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/neo4j_password neo4j:latest
```

***Note:*** Remove `--rm` if you want to keep the container after stopping it. Replace `podman` with `docker` if you use Docker.

... and import into Neo4J:

```
biokb_chebi import-neo4j -p neo4j_password
```

| Option | long       | Description        | default               |
| ------ | ---------- | ------------------ | --------------------- |
| -i     | --uri      | Neo4j database URI | bolt://localhost:7687 |
| -u     | --user     | Neo4j username     | neo4j                 |
| -p     | --password | Neo4j password     |                       |

http://localhost:7474  (user/password: neo4j/neo4j_password)

## How to run Neo4J

For the options "Run BioKb-ChEBI as ..."

1. [From command line](#from-command-line)
2. [As RESTful API server](#as-restful-api-server)

you need to run Neo4J separately.

If you have not already a Neo4j instance running, the easiest way is to run Neo4J as Podman/ Docker container.

For docker just replace `podman` with `docker` in the commands below.

```bash
podman run -d --rm --name biokb-neo4j -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/neo4j_password neo4j:latest
# Remove `--rm` if you want to keep the container after stopping it.
```

Neo4J is then available at:
http://localhost:7474  (user/password: neo4j/neo4j_password

Stop Neo4J with:

```bash
podman stop biokb-neo4j
```

if you have not used `--rm` above, you can restart Neo4J with:

```bash
podman start biokb-neo4j
```

## Query database with SQLAlchemy

In order to query the database with SQLAlchemy you can use the following code snippet:

```python
import os
from biokb_chebi import get_session
from biokb_chebi.db.models import Compound
os.environ.pop("CONNECTION_STR", None)  # to make sure no environment variable is used
with get_session() as session:
    results = session.query(Compound).filter(Compound.name.ilike("%glucose%")).limit(2)
    for row in results:
        print(f"Name: {row.ascii_name}, Name: {row.source}")
```

Output:

```console
Name: 1,2,3,4-tetrakis-O-galloyl-alpha-D-glucose, Name: KEGG COMPOUND
Name: 1-caffeoyl-beta-D-glucose, Name: KEGG COMPOUND
```

## UV installation/upgrade

It's strongly recommended to use a virtual environment to avoid conflicts with other Python packages. Best modern practice is to use [`uv`](https://docs.astral.sh/uv/) to create an isolated environment for your project. If you have not installed `uv` yet, you can do by:

***Linux / macOS***:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

***Windows***:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

If you have already `uv` on your system and want to **upgrade**:

```bash
uv self update
```
