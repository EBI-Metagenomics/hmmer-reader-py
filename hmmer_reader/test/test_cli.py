import importlib_resources as pkg_resources
from math import isinf, log

from click.testing import CliRunner

import hmmer_reader


def test_cli_frame():

    text = pkg_resources.read_text(hmmer_reader.test, "PF02545.hmm")
    runner = CliRunner()
    with runner.isolated_filesystem():

        def invoke(cmd):
            return runner.invoke(hmmer_reader.cli, cmd)

        with open("PF02545.hmm", "w") as f:
            f.write(text)

        r = invoke(["PF02545.hmm"])
        assert "STATS LOCAL MSV       -9.9559  0.70785" in r.stdout

        r = invoke(["PF02545.hmm", "--alphabet"])
        assert "ACDEFGHIKLMNPQRSTVWY" == r.stdout.strip()

        r = invoke(["PF02545.hmm", "--length"])
        assert "166" == r.stdout.strip()

        r = invoke(["PF02545.hmm", "--match", "0"])
        tbl = parse_table(r.stdout)
        assert tbl["A"] == 1.0
        assert tbl["C"] == 0.0

        r = invoke(["PF02545.hmm", "--match", "0"])
        tbl = parse_table(r.stdout)
        assert tbl["A"] == 1.0
        assert tbl["C"] == 0.0

        r = invoke(["PF02545.hmm", "--match", "1"])
        tbl = parse_table(r.stdout)
        assert abs(tbl["A"] - 0.063306327140559060) < 1e-7
        assert abs(tbl["C"] - 0.004970275538839500) < 1e-7

        r = invoke(["PF02545.hmm", "--match", "0", "--log"])
        tbl = parse_table(r.stdout)
        assert tbl["A"] == 0.0
        assert isinf(tbl["C"])

        r = invoke(["PF02545.hmm", "--match", "1", "--log"])
        tbl = parse_table(r.stdout)
        assert abs(tbl["A"] - log(0.063306327140559060)) < 1e-7
        assert abs(tbl["C"] - log(0.004970275538839500)) < 1e-7

        r = invoke(["PF02545.hmm", "--insert", "166"])
        tbl = parse_table(r.stdout)
        assert abs(tbl["M"] - 0.014308521644640306) < 1e-7
        assert abs(tbl["Y"] - 0.026916117721584094) < 1e-7

        r = invoke(["PF02545.hmm", "--insert", "166", "--log"])
        tbl = parse_table(r.stdout)
        assert abs(tbl["M"] - log(0.014308521644640306)) < 1e-7
        assert abs(tbl["Y"] - log(0.026916117721584094)) < 1e-7

        r = invoke(["PF02545.hmm", "--match", "5", "--sort"])
        assert "A 0.6014030" in r.stdout.strip().splitlines()[0].strip()
        assert "G 0.1542099" in r.stdout.strip().splitlines()[1].strip()


def test_cli_exclusive_opts():

    text = pkg_resources.read_text(hmmer_reader.test, "PF02545.hmm")
    runner = CliRunner()
    with runner.isolated_filesystem():

        def invoke(cmd):
            return runner.invoke(hmmer_reader.cli, cmd)

        with open("PF02545.hmm", "w") as f:
            f.write(text)

        r = invoke(["PF02545.hmm", "--match", "1", "--insert", "1"])
        assert r.exit_code == 1


def test_cli_out_of_range():

    text = pkg_resources.read_text(hmmer_reader.test, "PF02545.hmm")
    runner = CliRunner()
    with runner.isolated_filesystem():

        def invoke(cmd):
            return runner.invoke(hmmer_reader.cli, cmd)

        with open("PF02545.hmm", "w") as f:
            f.write(text)

        r = invoke(["PF02545.hmm", "--match", "167"])
        assert r.exit_code == 1


def parse_table(txt, sep=" "):
    txt = txt.strip()
    tbl = {}
    for line in txt.splitlines():
        k, v = line.split(sep, 1)
        tbl[k.strip()] = float(v.strip())
    return tbl
