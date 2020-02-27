import pathlib
from collections import OrderedDict
from math import inf
from typing import IO, Iterator, List, Union, Tuple


class ParsingError(Exception):
    pass


class EmptyBuffer(Exception):
    pass


class HMMERProfile:
    def __init__(self, file: IO[str]):
        self._header = ""
        self._metadata: List[Tuple[str, str]] = []
        self._alphabet: List[str] = []
        # model bg residue comp
        self._compo: OrderedDict = OrderedDict()
        self._match: List[OrderedDict] = []
        self._insert: List[OrderedDict] = []
        self._trans: List[OrderedDict] = []

        first_line = file.readline()
        if first_line == "":
            raise EmptyBuffer()

        self._header = strip(first_line)

        abc_line_found = False
        line = ""
        for i, line in enumerate(file):

            line = line.strip()
            if line.startswith("HMM "):
                abc_line_found = True
                break

            try:
                key, value = line.split(" ", 1)
            except ValueError:
                raise ParsingError(f"Could not parse line {i}: {line}")
            key = key.strip()
            value = value.strip()
            self._metadata.append((key, value))

        if not abc_line_found:
            raise ParsingError("Alphabet line not found.")

        self._read_alphabet(line)
        next(file)
        self._parse_matrix(file)

    @property
    def header(self):
        return self._header

    @property
    def metadata(self) -> List[Tuple[str, str]]:
        return self._metadata

    @property
    def compo(self) -> OrderedDict:
        return self._compo

    @property
    def alphabet(self):
        return self._alphabet

    @property
    def M(self):
        return len(self._match) - 1

    def match(self, i) -> OrderedDict:
        return _get_node_probs(self._match[i])

    def insert(self, i) -> OrderedDict:
        return _get_node_probs(self._insert[i])

    def trans(self, i) -> OrderedDict:
        return _get_node_probs(self._trans[i])

    def _read_alphabet(self, line):
        line = strip(line)
        self._alphabet = [v.strip() for v in line.split(" ")][1:]
        self._alphabet = "".join(self._alphabet)

    def _parse_matrix(self, fp):
        TRANS_DEF = ["MM", "MI", "MD", "IM", "II", "DM", "DD"]
        abc = self._alphabet

        line = strip(fp.readline()).split(" ")[1:]
        self._compo = OrderedDict([(a, num(b)) for a, b in zip(abc, line)])

        self._match.append(OrderedDict([(a, -inf) for a in abc]))
        self._match[0][abc[0]] = 0.0

        line = strip(fp.readline()).split(" ")[: len(abc)]
        self._insert.append(OrderedDict([(a, num(b)) for a, b in zip(abc, line)]))

        line = strip(fp.readline()).split(" ")[: len(abc)]
        self._trans.append(OrderedDict([(a, num(b)) for a, b in zip(TRANS_DEF, line)]))

        line = strip(fp.readline())
        while line != "//":
            line = line.split(" ")[1 : len(abc) + 1]
            self._match.append(OrderedDict([(a, num(b)) for a, b in zip(abc, line)]))

            line = strip(fp.readline()).split(" ")[: len(abc)]
            self._insert.append(OrderedDict([(a, num(b)) for a, b in zip(abc, line)]))

            line = strip(fp.readline()).split(" ")[: len(abc)]
            self._trans.append(
                OrderedDict([(a, num(b)) for a, b in zip(TRANS_DEF, line)])
            )

            line = strip(fp.readline())

    def __str__(self):
        msg = "File\n"
        msg += "----\n"
        msg += f"Header       {self.header}\n"
        msg += f"Alphabet     {self.alphabet}\n"
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
        return list(self)

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


def _get_node_probs(state) -> OrderedDict:
    return OrderedDict(list(state.items()))


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
    if v == "*":
        return -inf

    return -float(v)
