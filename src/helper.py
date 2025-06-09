# by Dr. Torben Menke https://entorb.net
# https://github.com/entorb/rememberthemilk

"""
RTM helper functions.
"""

# access to https://www.rememberthemilk.com tasks via their API
# API authentication documentation can be found at https://www.rememberthemilk.com/services/api/authentication.rtm
# list of available API methods can be fount at https://www.rememberthemilk.com/services/api/methods.rtm

import datetime as dt
import hashlib
import json
import re
import time
import tomllib
from pathlib import Path
from typing import cast
from zoneinfo import ZoneInfo

import pandas as pd
import requests

CACHE_DIR = Path(__file__).parent.parent / "cache"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# delete cache files older 1h
for file_path in CACHE_DIR.glob("*.json"):  # pragma: no cover
    if time.time() - file_path.stat().st_mtime > 3600:  # noqa: PLR2004
        file_path.unlink()


with (Path(__file__).parent / "rememberthemilk.toml").open("rb") as f:
    cfg = tomllib.load(f)["settings"]
    cfg = cast("dict[str, str]", cfg)

API_KEY = cfg["api_key"]
SHARED_SECRET = cfg["shared_secret"]
TOKEN = cfg["token"]
TZ = ZoneInfo(cfg["timezone"])
DATE_TODAY = dt.datetime.now(tz=TZ).date()

URL_RTM_BASE = "https://api.rememberthemilk.com/services/rest/"

PRIORITY_MAP = {"N": 1, "3": 1, "2": 2, "1": 4}

#
# helper functions 1: converters
#


def delete_cache() -> None:  # noqa: D103
    for file_path in CACHE_DIR.glob("*.json"):  # pragma: no cover
        file_path.unlink()


def dict_to_url_param(d: dict[str, str]) -> str:
    """
    Convert a dictionary of parameter to url parameter string.

    value pairs to an url conform list of key1=value1&key2=value2...
    """
    return "&".join("=".join(tup) for tup in d.items())


def json_parse_response(response_text: str) -> dict:
    """
    Convert response_text as JSON.

    Ensures that the response status is ok and drops that
    """
    try:
        d_json: dict = json.loads(response_text)
    except json.JSONDecodeError:  # pragma: no cover
        msg = f"Invalid JSON:\n{response_text}"
        raise ValueError(msg) from None
    if d_json["rsp"]["stat"] != "ok":  # pragma: no cover
        msg = f"Status not ok:\n{d_json}"
        raise ValueError(msg) from None
    del d_json["rsp"]["stat"]
    return d_json["rsp"]


def json_read(file_path: Path) -> list[dict[str, str]]:
    """
    Read JSON data from file.
    """
    with file_path.open(encoding="utf-8") as fh:
        json_data = json.load(fh)
    return json_data


def json_write(
    file_path: Path, json_data: list[dict[str, str]]
) -> None:  # pragma: no cover
    """
    Write JSON data to file.
    """
    with file_path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(json_data, fh, ensure_ascii=False, sort_keys=False, indent=2)


# def substr_between(s: str, s1: str, s2: str) -> str:
#     """
#     Return substring of s between strings s1 and s2.

#     s1 and s2 can be regular expressions
#     """
#     my_re = re.compile(s1 + "(.*)" + s2, flags=re.DOTALL)
#     my_matches = my_re.search(s)
#     if my_matches is None:
#         msg = f"can't find '{s1}'...'{s2}' in '{s}'"
#         raise Exception(msg)
#     out = my_matches.group(1)
#     return out


def gen_md5_string(s: str) -> str:
    """
    Generate MD5 hash.
    """
    m = hashlib.new("md5", usedforsecurity=False)
    m.update(s.encode("ascii"))
    return m.hexdigest()


def check_cache_file_available_and_recent(
    file_path: Path,
    max_age: int = 3500,
) -> bool:
    """Check if cache file exists and is recent."""
    cache_good = False
    if file_path.exists() and (time.time() - file_path.stat().st_mtime < max_age):
        cache_good = True
    return cache_good


def perform_rest_call(url: str) -> str:  # pragma: no cover
    """
    Perform a simple REST call to an url.

    if a cache file is more recent than 1 sec, wait for 1 sec
    Assert status = 200
    Return the response text.
    """
    # rate limit: 1 request per second
    for file_path in CACHE_DIR.glob("*.json"):
        if int(time.time()) == int(file_path.stat().st_mtime):
            print("sleeping for 1s to prevent rate limit")
            time.sleep(1)
            break

    resp = requests.get(url, timeout=3)
    if resp.status_code != 200:  # noqa: PLR2004
        msg = f"Bad response. status code:{resp.status_code}, text:\n{resp.text}"
        raise ValueError(msg) from None
    return resp.text


#
# helper functions 3: rtm specific
#


def gen_api_sig(param: dict[str, str]) -> str:
    """
    Generate the api_sig.

    according to https://www.rememberthemilk.com/services/api/authentication.rtm
    yxz=foo feg=bar abc=baz
      -> (1. sorting) abc=baz feg=bar yxz=foo
      -> (2. joining) abcbazfegbaryxzfoo -> MD5
    """
    s = "".join("".join(tup) for tup in sorted(param.items()))
    api_sig = gen_md5_string(SHARED_SECRET + s)
    return api_sig


def rtm_append_key_and_sig(d: dict[str, str]) -> dict[str, str]:
    """
    Add api_key (known) and api_sig (generated) to dict d.
    """
    d["api_key"] = API_KEY
    d["api_sig"] = gen_api_sig(d)
    return d


def rtm_append_key_and_token_and_sig(d: dict[str, str]) -> dict[str, str]:
    """
    Add api_key (known) auth_token (parameter) and api_sig (generated) to dict d.
    """
    d["api_key"] = API_KEY
    d["auth_token"] = TOKEN
    d["api_sig"] = gen_api_sig(d)
    return d


def rtm_call_method(method: str, arguments: dict[str, str]) -> dict:  # pragma: no cover
    """
    Call any rtm API method.

    request in json format
    asserts that the response is ok
    """
    param = {"method": method, "format": "json"}
    param.update(arguments)
    param_str = dict_to_url_param(rtm_append_key_and_token_and_sig(param))
    url = f"{URL_RTM_BASE}?{param_str}"
    response_text = perform_rest_call(url)
    d_json = json_parse_response(response_text)
    return d_json


# helper functions 4: lists


def get_lists_dict() -> dict[int, str]:
    """
    Return a dict of id -> name.
    """
    # print("\nRTM Lists")
    rtm_lists = get_lists()
    lists_dict: dict[int, str] = {}
    for el in rtm_lists:
        # {'id': '25825681', 'name': 'Name of my List', 'deleted': '0', 'locked': '0', 'archived': '0', 'position': '0', 'smart': '0', 'sort_order': '0'}  # noqa: E501
        lists_dict[int(el["id"])] = el["name"]
    # for my_tasks_per_list in rtm_lists:
    #     print(
    #         my_tasks_per_list["id"],
    #         my_tasks_per_list["smart"],
    #         my_tasks_per_list["name"],
    #     )
    return lists_dict


def get_lists() -> list[dict[str, str]]:
    """Fetch lists from RTM or cache if recent."""
    cache_file = CACHE_DIR / "lists.json"
    if check_cache_file_available_and_recent(file_path=cache_file, max_age=3600):
        lists = json_read(cache_file)
    else:  # pragma: no cover
        lists = get_rmt_lists()
        json_write(cache_file, lists)
    return lists


def get_rmt_lists() -> list[dict[str, str]]:  # pragma: no cover
    """Fetch lists from RTM."""
    json_data = rtm_call_method(method="rtm.lists.getList", arguments={})
    lists = json_data["lists"]["list"]
    lists = sorted(lists, key=lambda x: (x["smart"], x["name"]), reverse=False)
    return lists


# helper functions 5: tasks


def get_tasks_as_df(my_filter: str, lists_dict: dict[int, str]) -> pd.DataFrame:
    """Fetch filtered tasks from RTM or cache if recent."""
    tasks = get_tasks(my_filter)
    tasks_list_flat = flatten_tasks(rtm_tasks=tasks, lists_dict=lists_dict)
    tasks_list_flat2 = convert_task_fields(tasks_list_flat)
    df = tasks_to_df(tasks_list_flat2)
    return df


def get_tasks(my_filter: str) -> list[dict]:
    """Fetch filtered tasks from RTM or cache if recent."""
    # replace whitespaces by space
    my_filter = re.sub(r"\s+", " ", my_filter, flags=re.DOTALL)
    h = gen_md5_string(my_filter)
    cache_file = CACHE_DIR / f"tasks-{h}.json"
    if check_cache_file_available_and_recent(file_path=cache_file, max_age=3 * 3600):
        print(f"Using cache file: {cache_file}")
        tasks = json_read(cache_file)
    else:  # pragma: no cover
        tasks = get_rtm_tasks(my_filter)
        json_write(cache_file, tasks)
    return tasks


def get_rtm_tasks(my_filter: str) -> list[dict]:  # pragma: no cover
    # pragma: no cover
    """Fetch filtered tasks from RTM."""
    arguments = {
        "filter": my_filter,
        # "list_id": "45663479",  # filter by list ID
    }
    json_data = rtm_call_method(method="rtm.tasks.getList", arguments=arguments)
    tasks = json_data["tasks"]["list"]
    return tasks


def flatten_tasks(rtm_tasks: list[dict], lists_dict: dict[int, str]) -> list[dict]:
    """
    Flatten tasks.

    returns list of dicts
    """
    list_flat: list[dict] = []
    for tasks_per_list in rtm_tasks:
        # {'id': '45663480', 'taskseries': [...]}
        for taskseries in tasks_per_list["taskseries"]:
            # {'id': '524381810', 'created': '2023-12-03T20:04:47Z', 'modified': '2024-02-12T14:19:39Z', 'name': 'Name of my Taskseries', 'source': 'iphone-native', 'url': '', 'location_id': '', 'rrule': {'every': '0', '$t': 'FREQ=MONTHLY;INTERVAL=1;WKST=SU'}, 'tags': [], 'participants': [], 'notes': [], 'task': [{...}]}  # noqa: E501
            for task in taskseries["task"]:
                # {'id': '1008061846', 'due': '2024-01-02T23:00:00Z', 'has_due_time': '0', 'added': '2023-12-03T20:04:47Z', 'completed': '2024-02-12T14:19:36Z', 'deleted': '', 'priority': '3', 'postponed': '0', 'estimate': 'PT15M'}  # noqa: E501
                d = {
                    "list_id": tasks_per_list["id"],
                    "task_id": task["id"],
                    "list": lists_dict[int(tasks_per_list["id"])],
                    "name": taskseries["name"],
                    "due": task["due"],
                    "completed": task["completed"],
                    "prio": task["priority"],
                    "estimate": task["estimate"],
                    "postponed": task["postponed"],
                    "deleted": task["deleted"],
                }
                list_flat.append(d)

    return list_flat


def convert_task_fields(
    list_flat: list[dict],
) -> list[dict[str, str | int | dt.date]]:
    """
    Convert some fields to int or date."""
    list_flat2: list[dict[str, str | int | dt.date]] = []
    # {'list': 'PC', 'name': 'Name of my task', 'due': '2023-10-30T23:00:00Z', 'completed': '2023-12-31T09:53:50Z', 'priority': '2', 'estimate': 'PT30M', 'postponed': '0', 'deleted': ''}  # noqa: E501
    for task in list_flat:
        # IDs to int
        task["task_id"] = int(task["task_id"])
        task["list_id"] = int(task["list_id"])

        # postponed count to int
        task["postponed"] = int(task["postponed"])

        # estimate to minutes
        task["estimate"] = task_est_to_minutes(est=task["estimate"])

        # priority to int
        # N(=no)->1, 3->1, 2->2, 1 -> 4
        if task["prio"] in PRIORITY_MAP:
            task["prio"] = PRIORITY_MAP[task["prio"]]
        else:  # pragma: no cover
            msg = "Unknown priority:" + task["prio"]
            raise ValueError(msg) from None

        if len(task["completed"]) > 1:
            my_dt = dt.datetime.fromisoformat(
                task["completed"].replace("Z", " +00:00")
            ).astimezone(tz=TZ)
            task["completed_time"] = my_dt.strftime("%H:%M")
        else:
            task["completed_time"] = ""

        # due and completed to date, dropping timezone
        # "due": "2023-10-30T23:00:00Z"
        for field in ("due", "completed"):
            if len(task[field]) > 1:
                my_dt = dt.datetime.fromisoformat(task[field].replace("Z", " +00:00"))
                # convert to local time and than date only
                task[field] = my_dt.astimezone(tz=TZ).date()
            else:
                task[field] = None

        task = task_add_fields(task)  # noqa: PLW2901

        list_flat2.append(task)

    return list_flat2


def task_est_to_minutes(est: str) -> int | None:
    """Convert a time estimate string to minutes."""
    if len(est) == 0:
        return None

    task_time_min = 0
    if est.startswith("PT") and ("H" in est or "M" in est):
        est = est[2:]
        if "H" in est:
            s = est.split("H")
            task_time_min += int(s[0]) * 60
            est = s[1]
        if est.endswith("M"):
            task_time_min += int(est[:-1])
    else:  # pragma: no cover
        msg = "Unknown estimate:" + est
        raise ValueError(msg) from None

    return task_time_min


def task_add_fields(
    task: dict,
) -> dict[str, str | int | dt.date]:
    """
    Add some fields.

    Add overdue, overdue_prio, completed_week, url
    """
    # add overdue
    if task["due"] and task["completed"] and task["due"] <= task["completed"]:
        task["overdue"] = (task["completed"] - task["due"]).days
    elif task["due"] and not task["completed"] and task["due"] < DATE_TODAY:
        task["overdue"] = (DATE_TODAY - task["due"]).days
    else:
        task["overdue"] = None

    # overdue prio
    if task["overdue"]:
        task["overdue_prio"] = task["prio"] * task["overdue"]
    else:
        task["overdue_prio"] = None

    # add completed week
    if task["completed"]:
        year, week, _ = task["completed"].isocalendar()
        task["completed_week"] = dt.date.fromisocalendar(year, week, 1)
        del week, year
    else:
        task["completed_week"] = None

    # add url
    task["url"] = (
        f"https://www.rememberthemilk.com/app/#list/{task['list_id']}/{task['task_id']}"  # type: ignore
    )

    return task


def tasks_to_df(list_flat2: list[dict]) -> pd.DataFrame:
    """Convert tasks from list of dicts to Pandas DataFrame."""
    df = pd.DataFrame.from_records(list_flat2)
    df["overdue"] = df["overdue"].astype("Int64")
    df["overdue_prio"] = df["overdue_prio"].astype("Int64")
    df["estimate"] = df["estimate"].astype("Int64")

    return df


def df_name_url_to_html(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert name and url to html.

    name is html encoded first
    """
    # html encoding of column "name"
    df["name"] = df["name"].str.replace("&", "&amp;")
    df["name"] = df["name"].str.replace(">", "&gt;")
    df["name"] = df["name"].str.replace("<", "&lt;")
    df["name"] = df["name"].str.encode("ascii", "xmlcharrefreplace").str.decode("utf-8")
    # add url link to name
    df["name"] = '<a href="' + df["url"] + '" target="_blank">' + df["name"] + "</a>"
    return df


def df_to_html(
    df: pd.DataFrame, filename: str, *, index: bool = False
) -> None:  # pragma: no cover
    """Export DF to html."""
    print(f"Exporting to {filename}")

    html = df.to_html(
        index=index,
        render_links=False,
        escape=False,
        justify="center",
    )

    html = html.replace("<NA>", "")
    html = "<!DOCTYPE html>\n" + html

    (OUTPUT_DIR / filename).write_text(html)
