from importlib import import_module as _import_module

from . import data
from ._cli import cli
from ._misc import fetch_metadata, num_models
from ._reader import HMMERModel, HMMERParser, ParsingError, open_hmmer
from ._testit import test

try:
    from ._ffi import ffi

    del ffi
except Exception as e:
    _ffi_err = """
It is likely caused by a broken installation of this package.
Please, make sure you have a C compiler and try to uninstall
and reinstall the package again."""

    raise RuntimeError(str(e) + _ffi_err)

try:
    __version__ = getattr(_import_module("hmmer_reader._version"), "version", "x.x.x")
except ModuleNotFoundError:
    __version__ = "x.x.x"

__all__ = [
    "HMMERModel",
    "HMMERParser",
    "ParsingError",
    "__version__",
    "cli",
    "data",
    "fetch_metadata",
    "num_models",
    "open_hmmer",
    "test",
]
