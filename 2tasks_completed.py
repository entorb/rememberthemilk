"""
RTM tasks completed this year.

by Dr. Torben Menke https://entorb.net
"""

import datetime as dt

from helper import (
    DATE_TODAY,
    df_name_url_to_html,
    df_to_html,
    get_lists_dict,
    get_tasks_as_df,
)

if __name__ == "__main__":
    lists_dict = get_lists_dict()

    print("# RTM tasks completed this year")
    my_date = dt.date(DATE_TODAY.year, 1, 1)
    df = get_tasks_as_df(
        my_filter=f'CompletedAfter:{my_date.strftime("%d/%m/%Y")}',
        lists_dict=lists_dict,
    )
    df = df.sort_values(
        by=["completed", "prio", "name"], ascending=[False, False, True]
    )
    df = df.reset_index()

    df = df_name_url_to_html(df)
    df_to_html(
        df[
            [
                "name",
                "completed",
                # "completed_week",
                # "due",
                "overdue",
                "prio",
                "overdue_prio",
                "postponed",
                "estimate",
            ]
        ],
        "out-completed.html",
    )
    # df.to_excel("out-done-year.xlsx", index=False)

    df = df.groupby(["completed_week"]).agg(
        count=("completed_week", "count"),
        sum_prio=("prio", "sum"),
        sum_overdue_prio=("overdue_prio", "sum"),
        sum_estimate=("estimate", "sum"),
    )
    print(df)
