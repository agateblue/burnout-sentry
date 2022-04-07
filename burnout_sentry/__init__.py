import collections

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

    click.echo(f"Crunching numbers…")
    activity_params = {
        "off_weekdays": [5, 6],
        "workday_start": (8, 0),
        "workday_end": (20, 0),
    }
    contributors_activity = get_contributors_activity(
        get_transformed_commits(commits), **activity_params
    )

    for contributor, activity in contributors_activity:
        click.echo(
            f"{contributor} - {activity['total_commits']} commits - {activity['overtime_commits']} overtime commits"
        )


def get_transformed_commits(commits):
    """
    Return a subset of information from pydriller commits,
    makes testing easier because we can manipulate smaller and less-complex
    data structures
    """
    for commit in commits:
        yield {
            # we use author_date as the commit date instead of commit_date
            # because we're interested in the actual time the commit was performed
            # (vs the time it was applied on the branch, which may be different)
            "date": commit.author_date,
            "author_email": commit.author.email,
        }


def is_overtime_date(
    date,
    off_weekdays,
    workday_start,
    workday_end,
):
    return any(
        [
            date.weekday() in off_weekdays,
            (date.hour, date.minute) < workday_start,
            (date.hour, date.minute) > workday_end,
        ]
    )


def get_contributors_activity(
    commits,
    off_weekdays,
    workday_start,
    workday_end,
):
    per_contributor_data = collections.defaultdict(
        lambda: {"total_commits": 0, "overtime_commits": 0}
    )
    for commit in commits:
        contributor_data = per_contributor_data[commit["author_email"]]
        contributor_data["total_commits"] += 1
        is_overtime = is_overtime_date(
            commit["date"],
            off_weekdays=off_weekdays,
            workday_start=workday_start,
            workday_end=workday_end,
        )
        if is_overtime:
            contributor_data["overtime_commits"] += 1

    return [(contributor, data) for contributor, data in per_contributor_data.items()]


if __name__ == "__main__":
    cli()
