import pytest
import datetime

import burnout_sentry


@pytest.mark.parametrize(
    "date, expected",
    [
        # a friday, during office hours
        (datetime.datetime(2022, 4, 1, 10, 0), False),
        # a friday, late
        (datetime.datetime(2022, 4, 1, 23, 0), True),
        # a friday, very early
        (datetime.datetime(2022, 4, 1, 4, 0), True),
        # a saturday
        (datetime.datetime(2022, 4, 2, 12, 0), True),
        # a sunday
        (datetime.datetime(2022, 4, 2, 12, 0), True),
    ],
)
def test_is_overtime_date(date, expected):
    assert (
        burnout_sentry.is_overtime_date(
            date,
            off_weekdays=[5, 6],
            workday_start=(8, 0),
            workday_end=(20, 0),
        )
        == expected
    )


def test_get_contributors_activity():
    commits = [
        {
            "author_email": "me@agate.blue",
            # weekday, office hours
            "date": datetime.datetime(2022, 3, 4, 14, 0),
        },
        {
            "author_email": "me@agate.blue",
            # weekday, late
            "date": datetime.datetime(2022, 3, 4, 22, 0),
        },
        {
            "author_email": "me@agate.blue",
            # weekend
            "date": datetime.datetime(2022, 3, 5, 14, 0),
        },
        {
            # another contributor, aggregated separately
            "author_email": "valentin@entrouvert.com",
            "date": datetime.datetime(2021, 3, 4, 14, 0),
        },
    ]

    activity = burnout_sentry.get_contributors_activity(
        commits,
        off_weekdays=[5, 6],
        workday_start=(8, 0),
        workday_end=(20, 0),
    )

    expected = [
        {
            "contributor": "me@agate.blue",
            "total_commits": 3,
            "overtime_commits": 2,
        },
        {
            "contributor": "valentin@entrouvert.com",
            "total_commits": 1,
            "overtime_commits": 0,
        },
    ]

    assert activity == expected


@pytest.mark.parametrize(
    "field, expected_order",
    [
        ("none", [0, 1, 2, 3]),
        ("contributor", [0, 2, 3, 1]),
        ("total_commits", [0, 2, 1, 3]),
        ("overtime_commits", [2, 3, 0, 1]),
        ("overtime_ratio", [2, 3, 1, 0]),
    ],
)
def test_sort_activity(field, expected_order):
    activity = [
        {"contributor": "a@entrouvert.com", "total_commits": 12, "overtime_commits": 8},
        {
            "contributor": "d@entrouvert.com",
            "total_commits": 23,
            "overtime_commits": 15,
        },
        {"contributor": "b@entrouvert.com", "total_commits": 15, "overtime_commits": 1},
        {"contributor": "c@entrouvert.com", "total_commits": 47, "overtime_commits": 4},
    ]

    expected = [activity[i] for i in expected_order]

    assert burnout_sentry.sort_activity(activity, field) == expected
