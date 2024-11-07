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

DATE_START = dt.date(DATE_TODAY.year, 1, 1)
FILTER_COMPLETED = f"""
CompletedAfter:{DATE_START.strftime("%d/%m/%Y")}
AND NOT list:Taschengeld"""


if __name__ == "__main__":
    lists_dict = get_lists_dict()

    print("# RTM tasks completed this year")

    df = get_tasks_as_df(
        my_filter=FILTER_COMPLETED,
        lists_dict=lists_dict,
    )
    df = df.sort_values(
        by=["completed", "prio", "name"], ascending=[False, False, True]
    )
    df = df.reset_index()

    df = df_name_url_to_html(df)
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
    ]

    df_to_html(
        df[cols],
        "out-completed.html",
    )
    # df.to_excel(output_dir/"out-done-year.xlsx", index=False)

    df2 = df.groupby(["completed_week", "list"]).agg(
        count=("completed_week", "count"),
        sum_prio=("prio", "sum"),
        sum_overdue_prio=("overdue_prio", "sum"),
        sum_estimate=("estimate", "sum"),
    )
    print(df2)

    df_to_html(df2, "out-completed-week.html", index=True)
