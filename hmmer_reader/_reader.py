from math import exp, inf


def strip(s):
    import re

    return re.sub(" +", " ", s.strip())


TRANS_DEF = ["MM", "MI", "MD", "IM", "II", "DM", "DD"]


def num(v):
    from math import inf

    if v == "*":
        return inf

    return float(v)


class HMMEReader:
    def __init__(self, filepath):
        self._header = ""
        self._metadata = []
        self._alphabet = []
        # model bg residue comp
        self._compo = {}
        self._match = []
        self._insert = []
        self._trans = []

        with open(filepath, "r") as fp:
            self._header = strip(fp.readline())

            for line in fp:
                if line.startswith("HMM "):
                    break
                key, value = line.split(" ", 1)
                key = key.strip()
                value = value.strip()
                self._metadata.append((key, value))

            self._read_alphabet(line)
            next(fp)
            self._parse_matrix(fp)

    @property
    def header(self):
        return self._header

    @property
    def metadata(self):
        return self._metadata

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
        return {k: exp(-v) for k, v in self._match[i].items()}

    def insert(self, i):
        return {k: exp(-v) for k, v in self._insert[i].items()}

    def trans(self, i):
        return {k: exp(-v) for k, v in self._trans[i].items()}

    def _read_alphabet(self, line):
        line = strip(line)
        self._alphabet = [v.strip() for v in line.split(" ")][1:]
        self._alphabet = "".join(self._alphabet)

    def _parse_matrix(self, fp):
        line = strip(fp.readline()).split(" ")[1:]
        self._compo = {a: num(b) for a, b in zip(self._alphabet, line)}

        self._match.append({a: inf for a in self._alphabet})
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


def read(filepath):
    return HMMEReader(filepath)

