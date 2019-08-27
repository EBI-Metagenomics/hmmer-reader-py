try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib

    pkg_resources = importlib.import_module("importlib_resources")
    # Try backported to PY<37 `importlib_resources`.


def test_hmmer_reader():
    from hmmer_reader import read
    import hmmer_reader.test

    buffer = pkg_resources.open_text(hmmer_reader.test, "PF02545.hmm")
    file = read(buffer)
    assert file.M == 166
    assert file.alphabet == "ACDEFGHIKLMNPQRSTVWY"
    assert abs(file.match(2)["V"] - 0.1332937419515065) < 1e-6
    assert abs(file.insert(2)["V"] - 0.050530407257186674) < 1e-6
    assert abs(file.trans(83)["DD"] - 0.38897507965474065) < 1e-6
    assert file.compo["N"] == 3.21795

    buffer.close()
