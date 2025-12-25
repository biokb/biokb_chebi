from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("biokb_chebi")
except PackageNotFoundError:
    # Package is not installed (e.g., during local development)
    __version__ = "unknown"
