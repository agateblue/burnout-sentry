import json

import click
import pydriller
import tabulate


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


class Time(click.ParamType):
    name = "time"

    def convert(self, value, param, ctx):
        parts = value.split(":")
        try:
            # easiest case, a string such as 07:30 was provided
            hour, minute = parts
        except ValueError:
            # assume only hour was given and minute is 0
            hour, minute = parts[0], 0

        try:
            hour, minute = int(hour), int(minute)
        except (TypeError, ValueError):
            self.fail(f"{value!r} is not a time", param, ctx)
        return hour, minute


@cli.command("report")
@click.argument("repository", nargs=-1, required=True)
@click.option(
    "-s",
    "--sort",
    default="overtime_ratio",
    type=click.Choice(SORT_FIELDS),
    help="Sort the results using the given field (use in combination with --reverse to reverse the order)",
)
@click.option(
    "-r",
    "--reverse",
    is_flag=True,
    help="Reverse results order (use in combination with --sort)",
)
@click.option(
    "-f",
    "--format",
    default="rst",
    type=click.Choice(sorted(list(tabulate._table_formats.keys()) + ["json"])),
    help="Output format",
)
@click.option(
    "-l",
    "--limit",
    default=None,
    type=int,
    help="Truncate result list to the desired length",
)
@click.option(
    "-b",
    "--before",
    default=None,
    type=click.DateTime(),
    help="Restrict to commit authored before the given date (inclusive)",
)
@click.option(
    "-a",
    "--after",
    default=None,
    type=click.DateTime(),
    help="Restrict to commit authored after the given date (inclusive)",
)
@click.option(
    "-m",
    "--match",
    default=None,
    type=str,
    multiple=True,
    help="Restrict to author email matching one of the given strings",
)
@click.option(
    "--work-start",
    type=Time(),
    default="08:00",
    help="Start time for work days, e.g 08:30",
)
@click.option(
    "--work-end",
    type=Time(),
    default="20:00",
    help="End time for work days, e.g 18:30",
)
@click.option(
    "--off-weekday",
    type=int,
    multiple=True,
    default=[5, 6],
    help="Weekdays considered as off days. 0 is Monday, 6 is Sunday, defaults to Saturday and Sunday. May be provided multiple times.",
)
def report(
    repository,
    sort,
    reverse,
    format,
    limit,
    before,
    after,
    match,
    work_start,
    work_end,
    off_weekday,
):
    """
    Extract data from the given repositories and display a report for
    each contributor.

    Takes one or more repository path (URLs or paths to local directories).
    """
    click.echo(f"Getting commits from {len(repository)} repositories…")
    commits = pydriller.Repository(list(repository)).traverse_commits()

    click.echo(f"Crunching numbers…")
    activity_params = {
        "off_weekdays": off_weekday,
        "workday_start": work_start,
        "workday_end": work_end,
    }
    transformed_commits = get_transformed_commits(commits)
    transformed_commits = filter_commits(
        transformed_commits, after=after, before=before, match=match
    )
    contributors_activity = get_contributors_activity(
        transformed_commits, **activity_params
    )

    contributors_activity = sort_activity(contributors_activity, sort)

    if reverse:
        contributors_activity = reversed(contributors_activity)

    if limit:
        contributors_activity = list(contributors_activity)[:limit]

    if format == "json":
        return click.echo(
            json.dumps(list(contributors_activity), indent=2, sort_keys=True)
        )

    # construct data table for display in console
    headers = ["Contributor", "Total Commits", "Overtime Commits", "Overtime Ratio"]
    rows = [
        (
            a["contributor"],
            a["total_commits"],
            a["overtime_commits"],
            f"{a['overtime_commits'] / a['total_commits'] * 100:.0f} %",
        )
        for a in contributors_activity
    ]

    table = tabulate.tabulate(rows, headers, tablefmt=format)
    click.echo(table)


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


def filter_commits(commits, after=None, before=None, match=[]):
    for commit in commits:
        # XXX: we'll need to double check results on repos with
        # commiters from different timezones. Currently, we assume
        # the date passed in filters is in the same timezone as the
        # commit date
        if after and commit["date"] < after.replace(tzinfo=commit["date"].tzinfo):
            continue
        if before and commit["date"] > before.replace(tzinfo=commit["date"].tzinfo):
            continue
        if match and not any(
            (q.lower() in commit["author_email"].lower() for q in match)
        ):
            continue
        yield commit


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
    per_contributor_data = {}
    for commit in commits:
        contributor_data = per_contributor_data.get(
            commit["author_email"],
            {
                "total_commits": 0,
                "overtime_commits": 0,
                "contributor": commit["author_email"],
            },
        )
        contributor_data["total_commits"] += 1
        is_overtime = is_overtime_date(
            commit["date"],
            off_weekdays=off_weekdays,
            workday_start=workday_start,
            workday_end=workday_end,
        )
        if is_overtime:
            contributor_data["overtime_commits"] += 1

        per_contributor_data[commit["author_email"]] = contributor_data

    return [data for data in per_contributor_data.values()]


def sort_activity(activity, field):
    if field not in SORT_FIELDS:
        raise ValueError(f"{field} isn't a supported field for sorting")

    if field == "none":
        return activity
    if field in ["contributor", "total_commits", "overtime_commits"]:
        return sorted(activity, key=lambda v: v[field])
    if field == "overtime_ratio":
        return sorted(
            activity, key=lambda v: v["overtime_commits"] / v["total_commits"]
        )

    raise NotImplementedError(f"Sorting on {field} is not implemented")


if __name__ == "__main__":
    cli()
