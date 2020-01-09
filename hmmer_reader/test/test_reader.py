import importlib_resources as pkg_resources


def test_hmmer_reader():
    from hmmer_reader import read
    import hmmer_reader.test

    buffer = pkg_resources.open_text(hmmer_reader.test, "PF02545.hmm")
    hmmfile = read(buffer)

    hmmprof = next(hmmfile)
    assert hmmprof.header == "HMMER3/f [3.1b2 | February 2015]"
    assert hmmprof.metadata["LENG"] == "166"
    assert hmmprof.M == 166
    assert hmmprof.alphabet == "ACDEFGHIKLMNPQRSTVWY"
    assert abs(hmmprof.match(2)["V"] - -2.0152) < 1e-6
    assert abs(hmmprof.insert(2)["V"] - -2.98518) < 1e-6
    assert abs(hmmprof.trans(83)["DD"] - -0.94424) < 1e-6
    assert abs(hmmprof.compo["N"] + 3.21795) < 1e-6

    output = str(hmmprof)
    assert "SM    hmmsearch -Z 45638612 -E 1000 --cpu 4 HMM pfamseq" in output

    buffer.close()

def test_hmmer_prof():
    from hmmer_reader import read
    import hmmer_reader.test

    buffer = pkg_resources.open_text(hmmer_reader.test, "three-profs.hmm")
    hmmfile = read(buffer)

    hmmprof = next(hmmfile)
    assert hmmprof.header == "HMMER3/f [3.1b2 | February 2015]"
    assert hmmprof.metadata["LENG"] == "40"
    assert hmmprof.M == 40
    assert hmmprof.alphabet == "ACDEFGHIKLMNPQRSTVWY"
    assert abs(hmmprof.match(2)["V"] - -2.72416) < 1e-6
    assert abs(hmmprof.insert(2)["V"] - -2.98518) < 1e-6
    assert abs(hmmprof.trans(3)["DD"] - -0.9551) < 1e-6
    assert abs(hmmprof.compo["N"] - -3.18565) < 1e-6

    output = str(hmmprof)
    assert "SM    hmmsearch -Z 45638612 -E 1000 --cpu 4 HMM pfamseq" in output

    hmmprof = next(hmmfile)
    assert hmmprof.metadata["LENG"] == "235"

    hmmprof = next(hmmfile)
    assert hmmprof.metadata["LENG"] == "449"

    buffer.close()
