from ._cli import cli
from ._reader import HMMERParser, HMMERModel, ParsingError, open_hmmer
from ._testit import test

__version__ = "0.0.4"

__all__ = [
    "__version__",
    "open_hmmer",
    "test",
    "cli",
    "HMMERParser",
    "HMMERModel",
    "ParsingError",
]
