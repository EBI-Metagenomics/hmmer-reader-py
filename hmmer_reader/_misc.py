from pathlib import Path

__all__ = ["num_models"]


def num_models(filepath: Path) -> int:
    """
    Number of models in a HMMER3 ASCII file.
    """
    from subprocess import check_output

    output = check_output(f"grep 'HMMER3/f' {str(filepath)} | wc -l", shell=True)
    return int(output.strip())
