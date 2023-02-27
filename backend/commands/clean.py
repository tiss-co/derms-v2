import os

import click
from flask.cli import cli


@cli.command()
def clean():
    """Recursively remove *.pyc and *.pyo files."""

    for dirpath, _, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".pyc") or filename.endswith(".pyo"):
                filepath = os.path.join(dirpath, filename)
                click.echo(f"Removing {filepath}")
                os.remove(filepath)
