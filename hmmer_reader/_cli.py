import click
from ._click import command


def get_version():
    import re
    import hmmer_reader

    try:
        import importlib.resources as pkg_resources
    except ImportError:
        import importlib

        pkg_resources = importlib.import_module("importlib_resources")
        # Try backported to PY<37 `importlib_resources`.

    content = pkg_resources.read_text(hmmer_reader, "__init__.py")

    c = re.compile(r"__version__ *= *('[^']+'|\"[^\"]+\")")
    m = c.search(content)
    if m is None:
        return "unknown"

    return m.groups()[0][1:-1]


@click.command(cls=command(either=[("match", "insert")]))
@click.version_option(get_version())
@click.argument("filepath", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--match", help="Show the emission table of the given match state.", type=int
)
@click.option(
    "--insert", help="Show the emission table of the given insert state.", type=int
)
@click.option("--sort/--no-sort", help="Sort by probability.", default=False)
@click.option(
    "--log/--no-log",
    help="Show probabilities in negative log space: -log(p).",
    default=False,
)
def cli(filepath, match, insert, sort, log):
    """
    Show information about HMMER files.
    """
    from ._reader import read

    hmmer_file = read(filepath)
    if all([match is None, insert is None]):
        print(hmmer_file)
    elif match is not None:
        show(hmmer_file.alphabet, hmmer_file.match, match, sort, log)
    elif insert is not None:
        show(hmmer_file.alphabet, hmmer_file.insert, insert, sort, log)


def show(alphabet, node, idx, sort, log_space):

    try:
        values = [(a, node(idx, not log_space)[a]) for a in alphabet]
    except IndexError:
        raise click.ClickException(f"Index {idx} is higher than the model length.")
    if sort:
        values = sorted(values, key=lambda x: x[1], reverse=not log_space)

    for a, b in values:
        print(f"{a} {b:.18f}")
