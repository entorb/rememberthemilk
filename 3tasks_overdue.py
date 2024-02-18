"""
RTM tasks overdue.

by Dr. Torben Menke https://entorb.net
"""

from helper import (
    df_name_url_to_html,
    df_to_html,
    get_lists_dict,
    get_tasks_as_df,
)

if __name__ == "__main__":
    lists_dict = get_lists_dict()

    print("# RTM tasks overdue")
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

    cols = ["name", "list", "due", "overdue", "prio", "overdue_prio", "estimate"]

    print(df[cols])

    df = df_name_url_to_html(df)
    df_to_html(
        df[cols],
        "out-overdue.html",
    )
