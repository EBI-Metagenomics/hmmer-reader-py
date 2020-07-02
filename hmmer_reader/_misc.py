from pathlib import Path

__all__ = ["num_models", "fetch_metadata"]


def num_models(filepath: Path) -> int:
    """
    Number of models in a HMMER3 ASCII file.
    """
    from subprocess import check_output

    output = check_output(f"grep 'HMMER3/f' {str(filepath)} | wc -l", shell=True)
    return int(output.strip())


def fetch_metadata(filepath: Path):
    from pandas import read_csv
    import tempfile
    from subprocess import check_call

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpd = Path(tmpdir)
        name = tmpd / "NAME"
        acc = tmpd / "ACC"
        leng = tmpd / "LENG"
        alph = tmpd / "ALPH"

        cmd = f'grep -E "^(NAME  |ACC  |LENG  )" {filepath} | '
        cmd += "awk 'BEGIN { "
        cmd += f'patt["{name}"] = "^NAME  "; '
        cmd += f'patt["{acc}"] = "^ACC   "; '
        cmd += f'patt["{leng}"] = "^LENG  "; '
        cmd += f'patt["{alph}"] = "^ALPH  "; '
        cmd += "} { for (i in patt) if ($0 ~ patt[i]) print $2 > i; }'"
        check_call(cmd, shell=True)

        if not acc.exists():
            cmd = f"cat {name}"
            cmd += ' | awk \' { print "-" > "' + str(acc) + "\" } '"
            check_call(cmd, shell=True)

        meta = tmpd / "meta.tsv"
        check_call(f"paste {name} {acc} {leng} {alph} > {meta}", shell=True)
        return read_csv(
            meta,
            sep="\t",
            header=None,
            names=["NAME", "ACC", "LENG", "ALPH"],
            dtype={"NAME": str, "ACC": str, "LENG": int, "ALPH": str},
        )
