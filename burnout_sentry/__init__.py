import collections

import click
import pydriller


SORT_FIELDS = [
    "none",
    "contributor",
    "total_commits",
    "overtime_commits",
    "overtime_ratio",
]


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
@click.option(
    "-s",
    "--sort",
    default="overtime_ratio",
    type=click.Choice(SORT_FIELDS),
    help="Sort the results using the given field (use in combination with --reverse to reverse the order).",
)
@click.option(
    "-r",
    "--reverse",
    is_flag=True,
    help="Reverse results order (use in combination with --sort)",
)
def report(repository, sort, reverse):
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

    contributors_activity = sort_activity(contributors_activity, sort)

    if reverse:
        contributors_activity = sorted(contributors_activity, reverse=reverse)

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


def sort_activity(activity, field):
    if field not in SORT_FIELDS:
        raise ValueError(f"{field} isn't a supported field for sorting")

    if field == "none":
        return activity
    if field == "contributor":
        return sorted(activity, key=lambda v: v[0])
    if field == "total_commits":
        return sorted(activity, key=lambda v: v[1]["total_commits"])
    if field == "overtime_commits":
        return sorted(activity, key=lambda v: v[1]["overtime_commits"])
    if field == "overtime_ratio":
        return sorted(
            activity, key=lambda v: v[1]["overtime_commits"] / v[1]["total_commits"]
        )

    raise NotImplementedError(f"Sorting on {field} is not implemented")


if __name__ == "__main__":
    cli()
