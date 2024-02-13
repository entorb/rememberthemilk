"""
Playing with RememberTheMilk's API.
"""

# by Dr. Torben Menke https://entorb.net
# access to https://www.rememberthemilk.com tasks via their API
# API authentication documentation can be found at https://www.rememberthemilk.com/services/api/authentication.rtm
# list of available API methods can be fount at https://www.rememberthemilk.com/services/api/methods.rtm

from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from helper import (
    check_cache_file_available_and_recent,
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


def get_tasks(my_filter: str) -> list[dict[str, str]]:
    """Fetch filtered tasks from RTM or cache if recent."""
    cache_file = Path("cache/tasks.json")
    if check_cache_file_available_and_recent(file_path=cache_file, max_age=3 * 60):
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


def fix_task_fields(list_flat: list[dict[str, str]]) -> list[dict[str, str | int]]:
    """
    Convert some fields to int or date."""
    list_flat2: list[dict[str, str | int]] = []
    for task in list_flat:
        task["estimate"] = task["estimate"].replace("PT", "")
        if task["estimate"].endswith("M"):
            task["estimate"] = task["estimate"].replace("M", "")
            task["estimate"] = int(task["estimate"])  # type: ignore
        elif task["estimate"].endswith("H"):
            task["estimate"] = task["estimate"].replace("H", "")
            task["estimate"] = int(task["estimate"]) * 60  # type: ignore

        task["priority"] = int(task["priority"].replace("N", "0"))  # type: ignore

        task["postponed"] = int(task["postponed"])  # type: ignore

        list_flat2.append(task)  # type: ignore
    return list_flat2


def tasks_to_df(list_flat2: list[dict[str, str | int]]) -> pd.DataFrame:
    """Convert tasks from list of dicts to Pandas DataFrame."""
    df = pd.DataFrame.from_records(list_flat2)

    for col in ("due", "completed"):
        df[col] = (
            pd.to_datetime(df[col], format="%Y-%m-%dT%H:%M:%S%z")
            .dt.tz_convert(tz=TZ)
            .dt.tz_localize(None)
            .dt.date
        )

    # df["overdue"] = df["completed"] - df["due"]

    return df


if __name__ == "__main__":
    print("\nRTM Lists")
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
    rtm_tasks = get_tasks(
        my_filter="CompletedAfter:10/02/2023 CompletedBefore:01/01/2999"  #
    )
    rtm_tasks_flat = flatten_tasks(rtm_tasks, d_list_id_to_name)
    rtm_tasks_flat = fix_task_fields(rtm_tasks_flat)

    # for task in rtm_tasks_flat:
    #     print(task)

    df = tasks_to_df(rtm_tasks_flat)

    print(df)
    df.to_csv(
        "out.tsv",
        sep="\t",
        lineterminator="\n",
    )
    df.to_excel("out.xlsx", index=False)
