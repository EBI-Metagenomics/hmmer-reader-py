import importlib_resources as pkg_resources
import pytest


def test_hmmer_reader():
    from hmmer_reader import open_hmmer
    import hmmer_reader.test

    buffer = pkg_resources.open_text(hmmer_reader.test, "PF02545.hmm")
    hmmfile = open_hmmer(buffer)

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


def test_hmmer_prof():
    from hmmer_reader import open_hmmer
    import hmmer_reader.test

    buffer = pkg_resources.open_text(hmmer_reader.test, "three-profs.hmm")
    hmmfile = open_hmmer(buffer)

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
    from hmmer_reader import open_hmmer, ParsingError
    import hmmer_reader.test

    buffer = pkg_resources.open_text(hmmer_reader.test, "A0ALD9.fasta")
    hmmfile = open_hmmer(buffer)

    with pytest.raises(ParsingError):
        hmmfile.read_model()

    buffer.close()


def test_hmmer_reader_corrupted_file():
    from hmmer_reader import open_hmmer
    import hmmer_reader.test

    buffer = pkg_resources.open_text(hmmer_reader.test, "PF02545.hmm.br.corrupted")
    hmmfile = open_hmmer(buffer)

    with pytest.raises(UnicodeDecodeError):
        hmmfile.read_model()

    buffer.close()
