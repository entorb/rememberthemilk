"""Helper functions."""

import hashlib
import json
import time
from configparser import ConfigParser
from pathlib import Path

import requests

Path("cache").mkdir(exist_ok=True)
# delete cache files older 1h
for file_path in Path("cache/").glob("*.json"):
    if time.time() - file_path.stat().st_mtime > 3600:  # noqa: PLR2004
        file_path.unlink()


config = ConfigParser()
config.read("rememberthemilk.ini")
API_KEY = config.get("settings", "api_key")
SHARED_SECRET = config.get("settings", "shared_secret")
TOKEN = config.get("settings", "token")

URL_RTM_BASE = "https://api.rememberthemilk.com/services/rest/"

#
# helper functions 1: converters
#


def dict_to_url_param(d: dict[str, str]) -> str:
    """
    Convert a dictionary of parameter to url parameter string.

    value pairs to an url conform list of key1=value1&key2=value2...
    """
    return "&".join("=".join(tup) for tup in d.items())


def json_parse_response(response_text: str) -> dict[str, str]:
    """
    Convert response_text as JSON.

    Ensures that the response status is ok and drops that
    """
    try:
        d_json = json.loads(response_text)
    except json.JSONDecodeError:
        msg = f"E: invalid JSON:\n{response_text}"
        raise Exception(msg)  # noqa: B904, TRY002
    if d_json["rsp"]["stat"] != "ok":
        msg = f"E: status not ok:\n{d_json}"
        raise Exception(msg)  # noqa: TRY002
    del d_json["rsp"]["stat"]
    return d_json["rsp"]


def json_read(file_path: Path) -> list[dict[str, str]]:
    """
    Read JSON data from file.
    """
    with file_path.open(encoding="utf-8") as fh:
        json_data = json.load(fh)
    return json_data


def json_write(file_path: Path, json_data: list[dict[str, str]]) -> None:
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
#         msg = f"E: can't find '{s1}'...'{s2}' in '{s}'"
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


def perform_rest_call(url: str) -> str:
    """
    Perform a simple REST call to an url.

    Assert status = 200
    Return the response text.
    """
    resp = requests.get(url, timeout=3)
    if resp.status_code != 200:  # noqa: PLR2004
        msg = f"E: bad response. status code:{resp.status_code}, text:\n{resp.text}"
        raise Exception(msg)  # noqa: TRY002
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


def rtm_call_method(method: str, arguments: dict[str, str]) -> dict[str, str]:
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
