"""
Playing with RememberTheMilk's API.
"""

# by Dr. Torben Menke https://entorb.net
# access to https://www.rememberthemilk.com tasks via their API
# API authentication documentation can be found at https://www.rememberthemilk.com/services/api/authentication.rtm
# list of available API methods can be fount at https://www.rememberthemilk.com/services/api/methods.rtm

import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from helper import (
    check_cache_file_available_and_recent,
    gen_md5_string,
    json_read,
    json_write,
    rtm_call_method,
)

TZ = "Europe/Berlin"
ZONE = ZoneInfo(TZ)


def get_lists() -> list[dict[str, str]]:
    """Fetch lists from RTM or cache if recent."""
    cache_file = Path("cache/lists.json")
    if check_cache_file_available_and_recent(file_path=cache_file, max_age=3600):
        lists = json_read(cache_file)
    else:
        lists = get_rmt_lists()
        json_write(cache_file, lists)
    return lists


def get_rmt_lists() -> list[dict[str, str]]:
    """Fetch lists from RTM."""
    json_data = rtm_call_method(method="rtm.lists.getList", arguments={})

    lists = json_data["lists"]["list"]  # type: ignore
    lists = sorted(lists, key=lambda x: (x["smart"], x["name"]), reverse=False)  # type: ignore

    return lists  # type: ignore


def get_tasks_as_df(my_filter: str, d_list_id_to_name: dict[int, str]) -> pd.DataFrame:
    """Fetch filtered tasks from RTM or cache if recent."""
    tasks = get_tasks(my_filter)
    list_flat = flatten_tasks(rtm_tasks=tasks, d_list_id_to_name=d_list_id_to_name)
    list_flat2 = convert_task_fields(list_flat)
    df = tasks_to_df(list_flat2)
    return df


def get_tasks(my_filter: str) -> list[dict[str, str]]:
    """Fetch filtered tasks from RTM or cache if recent."""
    h = gen_md5_string(my_filter)
    cache_file = Path(f"cache/tasks-{h}.json")
    if check_cache_file_available_and_recent(file_path=cache_file, max_age=3 * 60):
        print(f"Using cache file: {cache_file}")
        tasks = json_read(cache_file)
    else:
        tasks = get_rtm_tasks(my_filter)
        json_write(cache_file, tasks)
    return tasks


def get_rtm_tasks(my_filter: str) -> list[dict[str, str]]:
    """Fetch filtered tasks from RTM."""
    arguments = {
        "filter": my_filter,
        # "list_id": "45663479",  # filter by list ID
    }
    json_data = rtm_call_method(method="rtm.tasks.getList", arguments=arguments)
    tasks = json_data["tasks"]["list"]  # type: ignore

    return tasks  # type: ignore


def flatten_tasks(
    rtm_tasks: list[dict[str, str]], d_list_id_to_name: dict[int, str]
) -> list[dict[str, str]]:
    """
    Flatten tasks.

    returns list of dicts
    """
    list_flat = []
    for tasks_per_list in rtm_tasks:
        # {'id': '45663480', 'taskseries': [...]}
        for taskseries in tasks_per_list["taskseries"]:
            # {'id': '524381810', 'created': '2023-12-03T20:04:47Z', 'modified': '2024-02-12T14:19:39Z', 'name': 'Name of my Taskseries', 'source': 'iphone-native', 'url': '', 'location_id': '', 'rrule': {'every': '0', '$t': 'FREQ=MONTHLY;INTERVAL=1;WKST=SU'}, 'tags': [], 'participants': [], 'notes': [], 'task': [{...}]}  # noqa: E501
            for task in taskseries["task"]:  # type: ignore
                # {'id': '1008061846', 'due': '2024-01-02T23:00:00Z', 'has_due_time': '0', 'added': '2023-12-03T20:04:47Z', 'completed': '2024-02-12T14:19:36Z', 'deleted': '', 'priority': '3', 'postponed': '0', 'estimate': 'PT15M'}  # noqa: E501
                d = {
                    "list_id": tasks_per_list["id"],  # type: ignore
                    "task_id": task["id"],  # type: ignore
                    "list": d_list_id_to_name[tasks_per_list["id"]],  # type: ignore
                    "name": taskseries["name"],  # type: ignore
                    "due": task["due"],  # type: ignore
                    "completed": task["completed"],  # type: ignore
                    "priority": task["priority"],  # type: ignore
                    "estimate": task["estimate"],  # type: ignore
                    "postponed": task["postponed"],  # type: ignore
                    "deleted": task["deleted"],  # type: ignore
                }
                list_flat.append(d)

    return list_flat


def convert_task_fields(  # noqa: C901, PLR0912
    list_flat: list[dict[str, str]],
) -> list[dict[str, str | int]]:
    """
    Convert some fields to int or date."""
    date_today = dt.datetime.now(tz=ZONE).date()
    list_flat2: list[dict[str, str | int]] = []
    for task in list_flat:
        # {'list': 'PC', 'name': 'Name of my task', 'due': '2023-10-30T23:00:00Z', 'completed': '2023-12-31T09:53:50Z', 'priority': '2', 'estimate': 'PT30M', 'postponed': '0', 'deleted': ''}  # noqa: E501
        task["estimate"] = task["estimate"].replace("PT", "")
        if task["estimate"].endswith("M"):
            task["estimate"] = task["estimate"].replace("M", "")
            task["estimate"] = int(task["estimate"])  # type: ignore
        elif task["estimate"].endswith("H"):
            task["estimate"] = task["estimate"].replace("H", "")
            task["estimate"] = int(task["estimate"]) * 60  # type: ignore

        # priority
        # 3 -> 1, 1->2, 2->2, N->1
        # no prio -> prio 1
        if task["priority"] == "N":
            task["priority"] = 1  # type: ignore
        elif task["priority"] == "1":
            task["priority"] = 3  # type: ignore
        elif task["priority"] == "2":
            task["priority"] = 2  # type: ignore
        elif task["priority"] == "3":
            task["priority"] = 1  # type: ignore
        else:
            raise Exception("E: unknown priority:" + task["priority"])  # noqa: TRY002

        task["postponed"] = int(task["postponed"])  # type: ignore

        # due and completed to date
        # "due": "2023-10-30T23:00:00Z"
        for field in ("due", "completed"):
            if len(task[field]) > 1:
                my_dt = dt.datetime.fromisoformat(task[field].replace("Z", " +00:00"))
                # convert to local time and than date only
                task[field] = my_dt.astimezone(tz=ZONE).date()  # type: ignore
            else:
                task[field] = None  # type: ignore

        # add overdue
        if task["due"] and task["completed"] and task["due"] <= task["completed"]:
            task["overdue"] = (task["completed"] - task["due"]).days  # type: ignore
        if task["due"] and not task["completed"] and task["due"] < date_today:  # type: ignore
            task["overdue"] = (date_today - task["due"]).days  # type: ignore
        else:
            task["overdue"] = None  # type: ignore

        # overdue prio
        if task["overdue"]:
            task["overdue priority"] = task["priority"] * task["overdue"]  # type: ignore
        else:
            task["overdue priority"] = None  # type: ignore

        # add completed week
        if task["completed"]:
            year = task["completed"].isocalendar()[0]  # type: ignore
            week = task["completed"].isocalendar()[1]  # type: ignore
            task["completed_week"] = dt.date.fromisocalendar(year, week, 1)  # type: ignore
            del week, year
        else:
            task["completed_week"] = None  # type: ignore

        # add url
        task[
            "url"
        ] = f'https://www.rememberthemilk.com/app/#list/{task["list_id"]}/{task["task_id"]}'  # type: ignore

        list_flat2.append(task)  # type: ignore

    return list_flat2


def tasks_to_df(list_flat2: list[dict[str, str | int]]) -> pd.DataFrame:
    """Convert tasks from list of dicts to Pandas DataFrame."""
    df = pd.DataFrame.from_records(list_flat2)
    df["overdue"] = df["overdue"].astype("Int64")

    return df


if __name__ == "__main__":
    # print("\nRTM Lists")
    rtm_lists = get_lists()
    d_list_id_to_name = {}
    for my_tasks_per_list in rtm_lists:
        # {'id': '25825681', 'name': 'Name of my List', 'deleted': '0', 'locked': '0', 'archived': '0', 'position': '0', 'smart': '0', 'sort_order': '0'}  # noqa: E501
        d_list_id_to_name[my_tasks_per_list["id"]] = my_tasks_per_list["name"]
    # for my_tasks_per_list in rtm_lists:
    #     print(
    #         my_tasks_per_list["id"],
    #         my_tasks_per_list["smart"],
    #         my_tasks_per_list["name"],
    #     )

    print("\nRTM tasks completed this year")
    my_date = dt.date(2024, 1, 1)
    df = get_tasks_as_df(
        my_filter=f'CompletedAfter:{my_date.strftime("%d/%m/%Y")}',
        d_list_id_to_name=d_list_id_to_name,
    )

    df = (
        df[["completed_week"]]
        .groupby(["completed_week"])
        .agg(count=("completed_week", "count"))
    )
    print(df)

    # Tasks overdue
    my_filter = """
dueBefore:Today
AND NOT completedAfter:01/01/2000
AND NOT list:Taschengeld
""".replace("\n", " ")
    df = get_tasks_as_df(
        my_filter=my_filter,
        d_list_id_to_name=d_list_id_to_name,
    )
    df = df.sort_values(by=["overdue priority"], ascending=False)

    # html encoding of column name only
    df["name"] = df["name"].str.encode("ascii", "xmlcharrefreplace").str.decode("utf-8")
    # add link to name
    df["name"] = "<a href='" + df["url"] + "' target='_blank'>" + df["name"] + "</a>"
    # export to html
    df[["name", "due", "overdue", "priority", "overdue priority"]].to_html(
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
    # df.to_excel("out.xlsx", index=False)
