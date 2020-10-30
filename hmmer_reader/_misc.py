import os
from collections import OrderedDict
from pathlib import Path
from tempfile import TemporaryFile

from numpy import int32
from pandas import DataFrame, read_csv

from ._reader import ParsingError

__all__ = ["num_models", "fetch_metadata"]


def num_models(filepath: Path) -> int:
    """
    Number of models in a HMMER3 ASCII file.
    """
    from subprocess import check_output

    output = check_output(f"grep 'HMMER3/f' {str(filepath)} | wc -l", shell=True)
    return int(output.strip())


def fetch_metadata(filepath: Path) -> DataFrame:
    from ._ffi import lib

    metadata = OrderedDict(
        [("NAME", str), ("ACC", str), ("LENG", int32), ("ALPH", str)]
    )

    if os.stat(filepath).st_size == 0:
        return DataFrame(columns=metadata.keys(), dtype=object)

    with TemporaryFile() as file, TemporaryFile() as estream:

        err: int = lib.meta_read(bytes(filepath), file, estream)
        if err != 0:
            estream.seek(0)
            emsg = estream.read().decode().strip()
            if err == 1:
                raise ParsingError(emsg)
            raise RuntimeError(emsg)

        file.seek(0)

        return read_csv(
            file,
            sep="\t",
            header=0,
            names=list(metadata.keys()),
            dtype=metadata,
        )
