"""Basic constants."""

import os
from pathlib import Path

ORGANIZATION = "biokb"
RESOURCE = "chebi"
HOME = str(Path.home())
PROJECT_FOLDER = os.path.join(HOME, f".{ORGANIZATION}", RESOURCE)
DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
DEFAULT_CONFIG_PATH: str = os.path.join(PROJECT_FOLDER, "config.ini")
EXPORT_FOLDER = os.path.join(DATA_FOLDER, "ttls")
ZIPPED_TTLS_PATH = os.path.join(DATA_FOLDER, "ttls.zip")
LOGS_FOLDER = os.path.join(DATA_FOLDER, "logs")  # where to store log files
