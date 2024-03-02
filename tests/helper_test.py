"""
Test helper functions.
"""  # noqa: INP001

# ruff: noqa: S101 D103 PLR2004
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

import pytest

# Add parent directory to the Python path, so we can run this file directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from helper import (
    convert_task_fields,
    df_name_url_to_html,
    dict_to_url_param,
    flatten_tasks,
    gen_md5_string,
    get_lists,
    get_lists_dict,
    get_tasks,
    json_parse_response,
    task_est_to_minutes,
    tasks_to_df,
)


def prepare_cache_lists() -> None:
    cache_source = Path("tests/test_data/lists.json")
    cache_target = Path("cache/lists.json")
    shutil.copyfile(cache_source, cache_target)


def prepare_cache_tasks() -> None:
    my_filter = "list:unit-tests"
    # l = get_tasks(my_filter=my_filter)
    h = gen_md5_string(my_filter)
    cache_source = Path(f"tests/test_data/tasks-{h}.json")
    cache_target = Path(f"cache/tasks-{h}.json")
    shutil.copyfile(cache_source, cache_target)


# TODO: use pytest fixtures instead
prepare_cache_lists()
prepare_cache_tasks()
# TODO: use pytest parameterize
# @pytest.mark.parametrize(
#     "name, input, expected_output",
#     [
#         ["Empty String", "", ""],
#         ["Empty String", " ", ""],


def test_dict_to_url_param() -> None:
    # Test empty dictionary
    assert dict_to_url_param({}) == ""

    # Test dictionary with single key-value pair
    assert dict_to_url_param({"key": "value"}) == "key=value"

    # Test dictionary with multiple key-value pairs
    assert (
        dict_to_url_param({"key1": "value1", "key2": "value2"})
        == "key1=value1&key2=value2"
    )


def test_gen_md5_string() -> None:
    my_filter = """
dueBefore:Today
AND NOT status:completed
AND NOT list:Taschengeld
"""
    assert gen_md5_string(my_filter) == "85d7cb53077789572349a3aabf8eb369"


def test_json_parse_response() -> None:
    # Test with single key-value pair
    assert json_parse_response('{"rsp": {"stat": "ok", "key1": "value1"}}') == {
        "key1": "value1"
    }


def test_get_lists() -> None:
    lists = get_lists()
    assert lists == [
        {
            "id": "50346883",
            "name": "unit-tests",
            "deleted": "0",
            "locked": "1",
            "archived": "0",
            "position": "-1",
            "smart": "0",
            "sort_order": "0",
        },
        {
            "id": "43953598",
            "name": "no Prio",
            "deleted": "0",
            "locked": "0",
            "archived": "0",
            "position": "0",
            "smart": "1",
            "sort_order": "0",
            "filter": "priority:none",
        },
    ]


def test_get_lists_dict() -> None:
    assert get_lists_dict() == {
        50346883: "unit-tests",
        43953598: "no Prio",
    }


def test_flatten_tasks() -> None:
    my_filter = "list:unit-tests"
    tasks = get_tasks(my_filter)
    lists_dict = get_lists_dict()
    tasks_list_flat = flatten_tasks(rtm_tasks=tasks, lists_dict=lists_dict)
    tasks_list_flat = sorted(
        tasks_list_flat, key=lambda row: (row["task_id"]), reverse=False
    )
    # from
    # json.dump(task_list_flat, open("tests/test_data/tasks.json", "w"), indent=2)
    # json.dump(
    #     data_expected, Path("tests/test_data/expected_tasks.json").open("w"), indent=2
    # )
    with Path("tests/test_data/expected_tasks.json").open() as fh:
        data_expected = json.load(fh)

    # length
    assert len(tasks_list_flat) == len(data_expected)
    # contents as string
    assert json.dumps(tasks_list_flat, indent=2) == json.dumps(data_expected, indent=2)


def test_convert_task_fields() -> None:
    my_filter = "list:unit-tests"
    tasks = get_tasks(my_filter)
    lists_dict = get_lists_dict()
    tasks_list_flat = flatten_tasks(rtm_tasks=tasks, lists_dict=lists_dict)
    tasks_list_flat = sorted(
        tasks_list_flat, key=lambda row: (row["task_id"]), reverse=False
    )

    tasks_list_flat2 = convert_task_fields(tasks_list_flat)
    assert tasks_list_flat2[3]["list_id"] == 50346883
    assert tasks_list_flat2[3]["task_id"] == 1029525734
    assert tasks_list_flat2[3]["prio"] == 2
    assert tasks_list_flat2[3]["estimate"] == 90
    assert tasks_list_flat2[3]["postponed"] == 0
    assert tasks_list_flat2[3]["due"] == dt.date(2024, 2, 28)
    assert tasks_list_flat2[3]["completed"] == dt.date(2024, 2, 24)
    assert (
        tasks_list_flat2[3]["url"]
        == "https://www.rememberthemilk.com/app/#list/50346883/1029525734"
    )


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [("", None), ("PT30M", 30), ("PT3H", 3 * 60), ("PT2H30M", 2 * 60 + 30)],
)
def test_task_est_to_minutes(test_input: str, expected: int) -> None:
    assert task_est_to_minutes(test_input) == expected


def test_get_tasks_as_df() -> None:
    my_filter = "list:unit-tests"
    tasks = get_tasks(my_filter)
    lists_dict = get_lists_dict()
    tasks_list_flat = flatten_tasks(rtm_tasks=tasks, lists_dict=lists_dict)
    tasks_list_flat = sorted(
        tasks_list_flat, key=lambda row: (row["task_id"]), reverse=False
    )
    tasks_list_flat2 = convert_task_fields(tasks_list_flat)

    df = tasks_to_df(tasks_list_flat2)
    assert len(df) == 6
    assert df["task_id"].loc[3] == 1029525734
    assert df["estimate"].loc[3] == 90


def test_df_name_url_to_html() -> None:
    my_filter = "list:unit-tests"
    tasks = get_tasks(my_filter)
    lists_dict = get_lists_dict()
    tasks_list_flat = flatten_tasks(rtm_tasks=tasks, lists_dict=lists_dict)
    tasks_list_flat = sorted(
        tasks_list_flat, key=lambda row: (row["task_id"]), reverse=False
    )
    tasks_list_flat2 = convert_task_fields(tasks_list_flat)
    df = tasks_to_df(tasks_list_flat2)

    df = df_name_url_to_html(df)
    assert (
        df["name"].loc[3]
        == '<a href="https://www.rememberthemilk.com/app/#list/50346883/1029525734" target="_blank">unit-test 1.1 completed</a>'  # noqa: E501
    )


def test_cleanup_cache_data() -> None:
    Path("cache/lists.json").unlink(missing_ok=True)

    my_filter = "list:unit-tests"
    h = gen_md5_string(my_filter)
    cache_target = Path(f"cache/tasks-{h}.json")
    cache_target.unlink(missing_ok=True)
