"""
Playing with RememberTheMilk's API.
"""

# by Dr. Torben Menke https://entorb.net
# access to https://www.rememberthemilk.com tasks via their API
# API authentication documentation can be found at https://www.rememberthemilk.com/services/api/authentication.rtm
# list of available API methods can be fount at https://www.rememberthemilk.com/services/api/methods.rtm

from helper import rtm_call_method


def rtm_get_lists() -> list[dict[str, str]]:
    """Fetch lists from RTM."""
    json_data = rtm_call_method(method="rtm.lists.getList", arguments={})

    lists = json_data["lists"]["list"]  # type: ignore
    lists = sorted(lists, key=lambda x: (x["smart"], x["name"]), reverse=False)  # type: ignore

    return lists  # type: ignore


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
                    "completed": task["completed"],  # type: ignore
                    "deleted": task["deleted"],  # type: ignore
                    "due": task["due"],  # type: ignore
                    "estimate": task["estimate"],  # type: ignore
                    "postponed": task["postponed"],  # type: ignore
                    "priority": task["priority"],  # type: ignore
                }
                list_flat.append(d)
    return list_flat


if __name__ == "__main__":
    print("\nRTM Lists")
    rtm_lists = rtm_get_lists()
    d_list_id_to_name = {}
    for my_tasks_per_list in rtm_lists:
        # {'id': '25825681', 'name': 'Name of my List', 'deleted': '0', 'locked': '0', 'archived': '0', 'position': '0', 'smart': '0', 'sort_order': '0'}  # noqa: E501
        d_list_id_to_name[my_tasks_per_list["id"]] = my_tasks_per_list["name"]
    for my_tasks_per_list in rtm_lists:
        print(
            my_tasks_per_list["id"],
            my_tasks_per_list["smart"],
            my_tasks_per_list["name"],
        )

    print("\nRTM tasks completed this year")
    rtm_tasks = get_rtm_tasks(
        my_filter="CompletedAfter:10/02/2024 CompletedBefore:01/01/2999"
    )
    rtm_tasks_flat = flatten_tasks(rtm_tasks, d_list_id_to_name)
    for task in rtm_tasks_flat:
        print(task)
