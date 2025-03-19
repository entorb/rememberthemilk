"""RTM tasks completed this year."""

# by Dr. Torben Menke https://entorb.net
# https://github.com/entorb/rememberthemilk

import datetime as dt

from pandas import DataFrame

from helper import (
    DATE_TODAY,
    df_name_url_to_html,
    df_to_html,
    get_lists_dict,
    get_tasks_as_df,
)

DATE_START = DATE_TODAY - dt.timedelta(days=365)
FILTER_COMPLETED = f"""
CompletedAfter:{DATE_START.strftime("%d/%m/%Y")}
AND NOT list:Taschengeld"""


def get_tasks_completed() -> DataFrame:  # noqa: D103
    lists_dict = get_lists_dict()
    df = get_tasks_as_df(
        my_filter=FILTER_COMPLETED,
        lists_dict=lists_dict,
    )
    df = df.sort_values(
        by=["completed", "prio", "name"], ascending=[False, False, True]
    )
    df = df.reset_index()

    cols = [
        "name",
        "list",
        "completed",
        "completed_week",
        # "due",
        "overdue",
        "prio",
        "overdue_prio",
        "postponed",
        "estimate",
        "url",
    ]
    df = df[cols]

    return df


def completed_week(df: DataFrame) -> DataFrame:  # noqa: D103
    df = (
        df.groupby(["completed_week", "list"])
        .agg(
            count=("completed_week", "count"),
            sum_prio=("prio", "sum"),
            sum_overdue_prio=("overdue_prio", "sum"),
            sum_estimate=("estimate", "sum"),
        )
        .sort_values(by=["completed_week", "list"], ascending=[False, True])
    )
    return df


if __name__ == "__main__":
    df = get_tasks_completed()

    print("# RTM tasks completed this year")

    df = df_name_url_to_html(df)

    df_to_html(
        df,
        "out-completed.html",
    )
    # df.to_excel(output_dir/"out-done-year.xlsx", index=False)

    df2 = completed_week(df)
    print(df2)

    df_to_html(df2, "out-completed-week.html", index=True)
