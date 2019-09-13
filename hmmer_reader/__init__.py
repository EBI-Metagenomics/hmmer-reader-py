from ._cli import cli
from ._reader import HMMEReader, read
from ._testit import test

__version__ = "0.0.1"

__all__ = ["__version__", "read", "test", "cli", "HMMEReader"]
