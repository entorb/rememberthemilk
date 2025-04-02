"""RTM tasks overdue."""

# by Dr. Torben Menke https://entorb.net
# https://github.com/entorb/rememberthemilk

from pandas import DataFrame

from helper import (
    df_name_url_to_html,
    df_to_html,
    get_lists_dict,
    get_tasks_as_df,
)

FILTER_OVERDUE = """
dueBefore:Today
AND NOT status:completed
AND NOT list:Taschengeld
"""


def get_tasks_overdue() -> DataFrame:  # noqa: D103
    lists_dict = get_lists_dict()

    df = get_tasks_as_df(
        my_filter=FILTER_OVERDUE,
        lists_dict=lists_dict,
    )
    df = df.sort_values(by=["overdue_prio"], ascending=False)
    df = df.reset_index()

    cols = ["name", "list", "due", "overdue", "prio", "overdue_prio", "estimate", "url"]
    df = df[cols]

    return df


def group_by_list(df: DataFrame) -> DataFrame:  # noqa: D103
    df = (
        df.groupby(["list"])
        .agg(
            count=("list", "count"),
            sum_prio=("prio", "sum"),
            sum_overdue_prio=("overdue_prio", "sum"),
            sum_estimate=("estimate", "sum"),
        )
        .sort_values(by=["list"], ascending=[True])
    )
    return df


if __name__ == "__main__":
    print("# RTM tasks overdue")
    df = get_tasks_overdue()

    print(df)

    df = df_name_url_to_html(df)
    df_to_html(
        df,
        "out-overdue.html",
    )
