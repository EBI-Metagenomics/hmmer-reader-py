import pathlib
from collections import OrderedDict
from math import inf
from typing import IO, Iterator, List, Union


class ParsingError(Exception):
    pass


class EmptyBuffer(Exception):
    pass


class HMMERProfile:
    def __init__(self, file):
        self._header = ""
        self._metadata = []
        self._alphabet = []
        # model bg residue comp
        self._compo = {}
        self._match = []
        self._insert = []
        self._trans = []

        first_line = file.readline()
        if first_line == "":
            raise EmptyBuffer()

        self._header = strip(first_line)

        abc_line_found = False
        for line in file:

            line = line.strip()
            if line.startswith("HMM "):
                abc_line_found = True
                break

            key, value = line.split(" ", 1)
            key = key.strip()
            value = value.strip()
            self._metadata.append((key, value))

        if not abc_line_found:
            raise ParsingError()

        self._read_alphabet(line)
        next(file)
        self._parse_matrix(file)

    @property
    def header(self):
        return self._header

    @property
    def metadata(self) -> OrderedDict:
        return OrderedDict(self._metadata)

    @property
    def compo(self):
        return self._compo

    @property
    def alphabet(self):
        return self._alphabet

    @property
    def M(self):
        return len(self._match) - 1

    def match(self, i):
        return self._get_node_probs(self._match[i])

    def insert(self, i):
        return self._get_node_probs(self._insert[i])

    def trans(self, i):
        return self._get_node_probs(self._trans[i])

    def _get_node_probs(self, state):
        return {k: v for k, v in state.items()}

    def _read_alphabet(self, line):
        line = strip(line)
        self._alphabet = [v.strip() for v in line.split(" ")][1:]
        self._alphabet = "".join(self._alphabet)

    def _parse_matrix(self, fp):
        TRANS_DEF = ["MM", "MI", "MD", "IM", "II", "DM", "DD"]

        line = strip(fp.readline()).split(" ")[1:]
        self._compo = {a: num(b) for a, b in zip(self._alphabet, line)}

        self._match.append({a: -inf for a in self._alphabet})
        self._match[0][self._alphabet[0]] = 0.0

        line = strip(fp.readline()).split(" ")[: len(self._alphabet)]
        self._insert.append({a: num(b) for (a, b) in zip(self._alphabet, line)})

        line = strip(fp.readline()).split(" ")[: len(self._alphabet)]
        self._trans.append({a: num(b) for (a, b) in zip(TRANS_DEF, line)})

        line = strip(fp.readline())
        while line != "//":
            line = line.split(" ")[1 : len(self._alphabet) + 1]
            self._match.append({a: num(b) for (a, b) in zip(self._alphabet, line)})

            line = strip(fp.readline()).split(" ")[: len(self._alphabet)]
            self._insert.append({a: num(b) for (a, b) in zip(self._alphabet, line)})

            line = strip(fp.readline()).split(" ")[: len(self._alphabet)]
            self._trans.append({a: num(b) for (a, b) in zip(TRANS_DEF, line)})

            line = strip(fp.readline())

    def __str__(self):
        msg = "File\n"
        msg += "----\n"
        msg += f"Header       {self._header}\n"
        msg += f"Alphabet     {self._alphabet}\n"
        msg += f"Model length {self.M}\n\n"

        msg += "Metadata\n"
        msg += "--------\n"
        for k, v in self._metadata:
            msg += k + " " * (6 - len(k)) + f"{v}\n"

        return msg[:-1]


class HMMERParser:
    def __init__(self, file: Union[str, pathlib.Path, IO[str]]):
        if isinstance(file, str):
            file = pathlib.Path(file)

        if isinstance(file, pathlib.Path):
            file = open(file, "r")

        self._file = file

    def read_profile(self) -> HMMERProfile:
        """
        Get the next profile.
        """
        try:
            return HMMERProfile(self._file)
        except EmptyBuffer:
            raise StopIteration

    def read_profiles(self) -> List[HMMERProfile]:
        """
        Get the list of all profiles.
        """
        return [item for item in self]

    def close(self):
        """
        Close the associated stream.
        """
        self._file.close()

    def __iter__(self) -> Iterator[HMMERProfile]:
        while True:
            try:
                yield self.read_profile()
            except StopIteration:
                return

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        del exception_type
        del exception_value
        del traceback
        self.close()


def open_hmmer(file: Union[str, pathlib.Path, IO[str]]) -> HMMERParser:
    """
    Open a HMMER file.

    Parameters
    ----------
    file : Union[str, pathlib.Path, IO[str]]
        File path or IO stream.

    Returns
    -------
    parser : HMMERParser
        HMMER parser.
    """
    return HMMERParser(file)


def strip(s):
    import re

    return re.sub(" +", " ", s.strip())


def num(v):
    from math import inf

    if v == "*":
        return -inf

    return -float(v)
