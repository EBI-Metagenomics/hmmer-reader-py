import gzip
import os
from io import StringIO
from pathlib import Path

import importlib_resources as pkg_resources
import pytest
from numpy import dtype

import hmmer_reader
from hmmer_reader import ParsingError, fetch_metadata, open_hmmer


def test_hmmer_reader():
    buffer = pkg_resources.open_binary(hmmer_reader.data, "PF02545.hmm.gz")

    content = gzip.decompress(buffer.read()).decode()
    hmmfile = open_hmmer(StringIO(content))

    hmm = hmmfile.read_model()
    assert hmm.header == "HMMER3/f [3.1b2 | February 2015]"
    assert dict(hmm.metadata)["LENG"] == "166"
    assert hmm.M == 166
    assert hmm.alphabet == "ACDEFGHIKLMNPQRSTVWY"
    assert abs(hmm.match(2)["V"] - -2.0152) < 1e-6
    assert abs(hmm.insert(2)["V"] - -2.98518) < 1e-6
    assert abs(hmm.trans(83)["DD"] - -0.94424) < 1e-6
    assert abs(hmm.compo["N"] + 3.21795) < 1e-6

    output = str(hmm)
    assert "SM    hmmsearch -Z 45638612 -E 1000 --cpu 4 HMM pfamseq" in output

    buffer.close()


def test_hmmer_reader_nt():
    buffer = pkg_resources.open_binary(hmmer_reader.data, "2OG-FeII_Oxy_3-nt.hmm.gz")

    content = gzip.decompress(buffer.read()).decode()
    hmmfile = open_hmmer(StringIO(content))

    hmm = hmmfile.read_model()
    assert hmm.header == "HMMER3/f [3.1b2 | February 2015]"
    assert dict(hmm.metadata)["LENG"] == "315"
    assert hmm.M == 315
    assert hmm.alphabet == "ACGT"
    assert abs(hmm.match(2)["A"] - -2.35771) < 1e-6
    assert abs(hmm.insert(2)["G"] - -1.38629) < 1e-6
    assert abs(hmm.trans(83)["DD"] - -0.40547) < 1e-6
    assert abs(hmm.compo["T"] - -1.50794) < 1e-6

    output = str(hmm)
    assert "DATE  Sun May 24 19:35:19 2015" in output

    buffer.close()


def test_hmmer_prof():
    buffer = pkg_resources.open_binary(hmmer_reader.data, "three-profs.hmm.gz")

    content = gzip.decompress(buffer.read()).decode()
    hmmfile = open_hmmer(StringIO(content))

    hmm = hmmfile.read_model()
    assert hmm.header == "HMMER3/f [3.1b2 | February 2015]"
    assert dict(hmm.metadata)["LENG"] == "40"
    assert hmm.M == 40
    assert hmm.alphabet == "ACDEFGHIKLMNPQRSTVWY"
    assert abs(hmm.match(2)["V"] - -2.72416) < 1e-6
    assert abs(hmm.insert(2)["V"] - -2.98518) < 1e-6
    assert abs(hmm.trans(3)["DD"] - -0.9551) < 1e-6
    assert abs(hmm.compo["N"] - -3.18565) < 1e-6

    output = str(hmm)
    assert "SM    hmmsearch -Z 45638612 -E 1000 --cpu 4 HMM pfamseq" in output

    hmm = hmmfile.read_model()
    assert dict(hmm.metadata)["LENG"] == "235"

    hmm = hmmfile.read_model()
    assert dict(hmm.metadata)["LENG"] == "449"

    buffer.close()


def test_hmmer_reader_invalid_file():
    buffer = pkg_resources.open_text(hmmer_reader.data, "A0ALD9.fasta")
    hmmfile = open_hmmer(buffer)

    with pytest.raises(ParsingError):
        hmmfile.read_model()

    buffer.close()


def test_hmmer_reader_corrupted_file():
    buffer = pkg_resources.open_text(hmmer_reader.data, "PF02545.hmm.br.corrupted")
    hmmfile = open_hmmer(buffer)

    with pytest.raises(UnicodeDecodeError):
        hmmfile.read_model()

    buffer.close()


def test_hmmer_reader_fetch_metadata1(tmp_path: Path):
    buffer = pkg_resources.open_binary(hmmer_reader.data, "PF02545.hmm.gz")

    content = gzip.decompress(buffer.read()).decode()
    os.chdir(tmp_path)
    with open("db.hmm", "w") as file:
        file.write(content)

    df = fetch_metadata(tmp_path / "db.hmm")
    assert df.shape == (1, 4)
    assert df["NAME"].values[0] == "Maf"
    assert df["ACC"].values[0] == "PF02545.14"
    assert df["LENG"].values[0] == 166
    assert df["ALPH"].values[0] == "amino"

    assert df["NAME"].dtype is dtype("O")
    assert df["ACC"].dtype is dtype("O")
    assert df["LENG"].dtype is dtype("int32")
    assert df["ALPH"].dtype is dtype("O")

    assert tuple(df.columns) == ("NAME", "ACC", "LENG", "ALPH")


def test_hmmer_reader_fetch_metadata2(tmp_path: Path):
    buffer = pkg_resources.open_binary(hmmer_reader.data, "three-profs.hmm.gz")

    content = gzip.decompress(buffer.read()).decode()
    os.chdir(tmp_path)
    with open("db.hmm", "w") as file:
        file.write(content)

    df = fetch_metadata(tmp_path / "db.hmm")
    assert df.shape == (3, 4)

    assert df["NAME"].values[0] == "1-cysPrx_C"
    assert df["ACC"].values[0] == "PF10417.9"
    assert df["LENG"].values[0] == 40
    assert df["ALPH"].values[0] == "amino"

    assert df["NAME"].values[1] == "120_Rick_ant"
    assert df["ACC"].values[1] == "PF12574.8"
    assert df["LENG"].values[1] == 235
    assert df["ALPH"].values[1] == "amino"

    assert df["NAME"].values[2] == "12TM_1"
    assert df["ACC"].values[2] == "PF09847.9"
    assert df["LENG"].values[2] == 449
    assert df["ALPH"].values[2] == "amino"

    assert df["NAME"].dtype is dtype("O")
    assert df["ACC"].dtype is dtype("O")
    assert df["LENG"].dtype is dtype("int32")
    assert df["ALPH"].dtype is dtype("O")

    assert tuple(df.columns) == ("NAME", "ACC", "LENG", "ALPH")


# def test_hmmer_reader_fetch_metadata_corrupted1(tmp_path: Path):
#     buffer = pkg_resources.open_binary(hmmer_reader.data, "corrupted1.hmm.gz")

#     content = gzip.decompress(buffer.read()).decode()
#     os.chdir(tmp_path)
#     with open("db.hmm", "w") as file:
#         file.write(content)

#     df = fetch_metadata(tmp_path / "db.hmm")
#     breakpoint()
#     assert df.shape == (3, 4)

#     assert df["NAME"].values[0] == "1-cysPrx_C"
#     assert df["ACC"].values[0] == "PF10417.9"
#     assert df["LENG"].values[0] == 40
#     assert df["ALPH"].values[0] == "amino"

#     assert df["NAME"].values[1] == "120_Rick_ant"
#     assert df["ACC"].values[1] == "PF12574.8"
#     assert df["LENG"].values[1] == 235
#     assert df["ALPH"].values[1] == "amino"

#     assert df["NAME"].values[2] == "12TM_1"
#     assert df["ACC"].values[2] == "PF09847.9"
#     assert df["LENG"].values[2] == 449
#     assert df["ALPH"].values[2] == "amino"

#     assert df["NAME"].dtype is dtype("O")
#     assert df["ACC"].dtype is dtype("O")
#     assert df["LENG"].dtype is dtype("int32")
#     assert df["ALPH"].dtype is dtype("O")

#     assert tuple(df.columns) == ("NAME", "ACC", "LENG", "ALPH")
