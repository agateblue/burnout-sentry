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
@click.argument("repository", nargs=-1, required=True)
def report(repository):
    """
    Extract data from the given repositories and display a report for
    each contributor.

    Takes one or more repository path (URLs or paths to local directories).
    """
    click.echo(f"Getting commits from {len(repository)} repositories…")
    commits = pydriller.Repository(list(repository)).traverse_commits()

    click.echo(f"Extracting data from {len(list(commits))} commits…")


if __name__ == "__main__":
    cli()
