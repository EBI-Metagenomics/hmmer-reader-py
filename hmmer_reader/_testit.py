def test(verbose=True):
    """
    Run tests to verify this package's integrity.

    Parameters
    ----------
    verbose : bool
        ``True`` to show diagnostic. Defaults to ``True``.

    Returns
    -------
    int
        Exit code: ``0`` for success.
    """

    args = ["--doctest-modules", "--doctest-plus"]
    if not verbose:
        args += ["--quiet"]

    args += ["--pyargs", __name__.split(".")[0]]

    return __import__("pytest").main(args)
