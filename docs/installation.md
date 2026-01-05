# Installation

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


## Quick Start


```bash
biokb_chebi run-api
```

http://localhost:8000/docs#/

1. [Import data](http://localhost:8000/docs#/Database%20Management/import_data_import_data__post)
2. [Export ttls](http://localhost:8000/docs#/Database%20Management/get_report_export_ttls__get)
3. [Import Neo4J](http://localhost:8000/docs#/Database%20Management/import_neo4j_import_neo4j__get)

### Create turtles and import into Neo4J

For docker just replace `podman` with `docker` in the commands below.

```bash
biokb_chebi create-ttls
podman run -d --rm --name biokb-neo4j -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/neo4j_password neo4j:latest
# Remove `--rm` if you want to keep the container after stopping it.
# wait a bit until Neo4J is started
biokb_chebi import-neo4j -p neo4j_password
```

http://localhost:7474  (user/password: neo4j/neo4j_password)


```bash
podman stop biokb-neo4j
```


### Run as Podman/ Docker container

For docker just replace `podman` with `docker` in the commands below.

Build & run with Podman:
```bash
git clone https://github.com/biokb/biokb_chebi.git
cd biokb_chebi
podman build -t biokb_chebi .
podman run -d --rm --name biokb_chebi -p 8000:8000 biokb_chebi
```

- Login: admin  
- Password: admin

With environment variable for user and password for more security:
```bash
podman run -d --rm --name biokb_chebi -p 8000:8000 -e API_PASSWORD=your_secure_password -e API_USER=your_secure_user biokb_chebi
```

http://localhost:8000/docs

On the website:
1. [Import data](http://localhost:8000/docs#/Database%20Management/import_data_import_data__post)
2. http://localhost:8000/docs#/Database%20Management/get_report_export_ttls__get

Neo4j import in this context is not possible because Neo4J is not running as service.


### Run as Podman/Docker networked containers with Neo4J and MySQL

Build & run with Docker:
```bash
git clone https://github.com/biokb/biokb_chebi.git
cd biokb_chebi
podman-compose -f docker-compose.db_neo.yml --env-file .env_template up -d

```
http://localhost:8000/docs

stop with:
```bash
docker stop biokb_chebi
```

rerun with:
```bash
docker start biokb_chebi
```

### Run with MySQL and Neo4J as podman-compose services

```bash
git clone https://github.com/biokb/biokb_chebi.git
cd biokb_chebi 
podman-compose -f docker-compose.db_neo.yml --env-file .env_template up -d
podman-compose --env-file .env_template up -d
```

In production copy .env_template to .env and use secure passwords (and skip `--env-file .env_template` in the last command)!

```bash
podman-compose -f docker-compose.db_neo.yml --env-file .env_template up -d
podman-compose --env-file .env_template up -d
```

http://localhost:8001/docs

On the website:
1. [Import data](http://localhost:8001/docs#/Database%20Management/import_data_import_data__post)
2. [Export ttls](http://localhost:8001/docs#/Database%20Management/get_report_export_ttls__get)
3. [Import Neo4J](http://localhost:8001/docs#/Database%20Management/import_neo4j_import_neo4j__get)


## CLI
Install with
```
pip install biokb_chebi
```

### Import data into relational database

***Usage:*** `biokb_chebi import-data [OPTIONS]`

```
biokb_chebi import-data
```

-> SQLite database in `~/.biokb/biokb.db`. Open with e.g. [DB Browser for SQLite](https://sqlitebrowser.org/)

| Option | long | Description | default |
|--------|------|-------------|---------|
| -f     | --force-download | Force re-download of the source file | False   |
| -k     | --keep-files     | Keep downloaded source files after import | False   |
| -c     | --connection-string TEXT | SQLAlchemy engine URL | sqlite:///chebi.db | 

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

| Option | long | Description | default |
|--------|------|-------------|---------|
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

| Option               | long                | Description          | default                  |
|----------------------|---------------------|----------------------|--------------------------|
|-i | --uri | Neo4j database URI  | bolt://localhost:7687    |
| -u                    | --user              | Neo4j username        | neo4j                    |
| -p                   | --password          | Neo4j password         | |


http://localhost:7474  (user/password: neo4j/neo4j_password)


For testing you can install from TestPyPI:
```bash
uv venv
source venv/bin/activate
uv pip install --no-cache-dir -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ biokb-chebi==0.1.0
```