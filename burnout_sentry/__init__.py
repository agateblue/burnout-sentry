import click

import pydriller


@click.group()
def cli():
    """
    A CLI tool to extract data from git repositories and detect possible
    burnout-situations, typically a contributor working on late hours
    or weekends.
    """
    pass


@cli.command("report")
def report():
    """
    Extract data from the given repositories and display a report for
    each contributor.
    """
    click.echo("Hello world")


if __name__ == "__main__":
    cli()
