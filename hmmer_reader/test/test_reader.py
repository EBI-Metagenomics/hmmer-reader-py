import importlib_resources as pkg_resources


def test_hmmer_reader():
    from hmmer_reader import read
    import hmmer_reader.test

    buffer = pkg_resources.open_text(hmmer_reader.test, "PF02545.hmm")
    hmmfile = read(buffer)

    assert hmmfile.header == "HMMER3/f [3.1b2 | February 2015]"
    assert hmmfile.metadata["LENG"] == "166"
    assert hmmfile.M == 166
    assert hmmfile.alphabet == "ACDEFGHIKLMNPQRSTVWY"
    assert abs(hmmfile.match(2)["V"] - -2.0152) < 1e-6
    assert abs(hmmfile.insert(2)["V"] - -2.98518) < 1e-6
    assert abs(hmmfile.trans(83)["DD"] - -0.94424) < 1e-6
    assert abs(hmmfile.compo["N"] + 3.21795) < 1e-6

    output = str(hmmfile)
    assert "SM    hmmsearch -Z 45638612 -E 1000 --cpu 4 HMM pfamseq" in output

    buffer.close()
