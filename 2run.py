"""
RTM tasks completed this year.

by Dr. Torben Menke https://entorb.net
"""

import datetime as dt

from helper import (
    get_lists_dict,
    get_tasks_as_df,
)

if __name__ == "__main__":
    lists_dict = get_lists_dict()

    print("\nRTM tasks completed this year")
    my_date = dt.date(2024, 1, 1)
    df = get_tasks_as_df(
        my_filter=f'CompletedAfter:{my_date.strftime("%d/%m/%Y")}',
        lists_dict=lists_dict,
    )
    df = df.sort_values(by=["completed"], ascending=False)
    df = df.drop(columns=["list_id", "task_id", "url"])

    df.to_excel("out-done-year.xlsx", index=False)

    df = df.groupby(["completed_week"]).agg(
        count=("completed_week", "count"),
        sum_prio=("prio", "sum"),
        sum_overdue_prio=("overdue_prio", "sum"),
        sum_estimate=("estimate", "sum"),
    )
    print(df)

    print("\nRTM tasks overdue")
    my_filter = """
dueBefore:Today
AND NOT status:completed
AND NOT list:Taschengeld
"""
    df = get_tasks_as_df(
        my_filter=my_filter,
        lists_dict=lists_dict,
    )
    df = df.sort_values(by=["overdue_prio"], ascending=False)
    df = df.reset_index()

    print(df[["name", "due", "overdue", "prio", "overdue_prio"]])
    # html encoding of column name only
    df["name"] = df["name"].str.encode("ascii", "xmlcharrefreplace").str.decode("utf-8")
    # add link to name
    df["name"] = "<a href='" + df["url"] + "' target='_blank'>" + df["name"] + "</a>"
    # export to html
    df = df[["name", "due", "overdue", "prio", "overdue_prio", "estimate"]]
    df.to_html(
        "out-overdue.html",
        index=False,
        render_links=False,
        escape=False,
        justify="center",
    )

    # print(df)
    # df.to_csv(
    #     "out.tsv",
    #     sep="\t",
    #     lineterminator="\n",
    # )
