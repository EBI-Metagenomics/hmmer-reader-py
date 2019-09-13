import click
from ._click import command


def get_version():
    import re
    import hmmer_reader
    import importlib_resources as pkg_resources

    content = pkg_resources.read_text(hmmer_reader, "__init__.py")
    c = re.compile(r"__version__ *= *('[^']+'|\"[^\"]+\")")
    m = c.search(content)
    return m.groups()[0][1:-1]


@click.command(
    cls=command(either=[("alphabet", "length", "match", "insert")]),
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.version_option(get_version())
@click.argument("filepath", type=click.Path(exists=True, dir_okay=False))
@click.option("--alphabet", help="Show the alphabet.", is_flag=True, default=None)
@click.option("--length", help="Show the model length.", is_flag=True, default=None)
@click.option(
    "--match", help="Show the emission table of the given match state.", type=int
)
@click.option(
    "--insert", help="Show the emission table of the given insert state.", type=int
)
@click.option("--sort/--no-sort", help="Sort by probability.", default=False)
@click.option(
    "--log/--no-log", help="Show probabilities in log space: log(p).", default=False
)
def cli(filepath, alphabet, length, match, insert, sort, log):
    """
    Show information about HMMER files.
    """
    from ._reader import read

    hmmer = read(filepath)
    if all([not alphabet, not length, match is None, insert is None]):
        print(hmmer)
    elif alphabet:
        print(hmmer.alphabet)
    elif length:
        print(hmmer.M)
    elif match is not None:
        show(hmmer.alphabet, hmmer.match, match, sort, log)
    elif insert is not None:
        show(hmmer.alphabet, hmmer.insert, insert, sort, log)


def show(alphabet, node, idx, sort, log_space):

    try:
        values = [(a, node(idx, log_space)[a]) for a in alphabet]
    except IndexError:
        raise click.ClickException(f"Index {idx} is higher than the model length.")
    if sort:
        values = sorted(values, key=lambda x: x[1], reverse=not log_space)

    for a, b in values:
        print(f"{a} {b:.18f}")
