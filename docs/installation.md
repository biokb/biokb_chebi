## Installation

## Without Podman/Docker

If [uv](https://docs.astral.sh/uv/) is installed:

```bash
uv venv
source .venv/bin/activate
uv pip install biokb_chebi
```

Go to [Run BioKb-ChEBI](run_the_pipeline.md) to learn how to execute the pipeline (after installation).

### With Podman/Docker

If you have [docker](https://www.docker.com/get-started) or [podman](https://podman.io/getting-started/installation) on your system, the easiest way to run all components (relational database, RESTful API server, phpMyAdmin GUI) is to use networked containers with `podman-compose`/`docker-compose`.

```bash
git clone https://github.com/biokb/biokb_chebi.git
cd biokb_chebi
python3 -m venv .venv
source .venv/bin/activate
pip install podman-compose
podman-compose -f docker-compose.yml --env-file .env_template up -d
```

Tip: Change the default passwords in the `.env_template` file before starting the containers for better security.