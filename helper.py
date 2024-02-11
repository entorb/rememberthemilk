"""Helper functions."""

import hashlib
import re
from configparser import ConfigParser

import requests

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


def perform_rest_call(url: str) -> str:
    """
    Perform a simple REST call to an url.

    Return the response text.
    """
    resp = requests.get(url, timeout=3)
    if resp.status_code != 200:  # noqa: PLR2004
        msg = f"E: bad response. status code:{resp.status_code}, text:\n{resp.text}"
        raise Exception(msg)  # noqa: TRY002
    return resp.text


def substr_between(s: str, s1: str, s2: str) -> str:
    """
    Return substring of s between strings s1 and s2.

    s1 and s2 can be regular expressions
    """
    my_re = re.compile(s1 + "(.*)" + s2, flags=re.DOTALL)
    my_matches = my_re.search(s)
    if my_matches is None:
        msg = f"E: can't find '{s1}'...'{s2}' in '{s}'"
        raise Exception(msg)  # noqa: TRY002
    out = my_matches.group(1)
    return out


def gen_md5_string(s: str) -> str:
    """
    Generate MD5 hash.
    """
    m = hashlib.new("md5", usedforsecurity=False)
    m.update(s.encode("ascii"))
    return m.hexdigest()


#
# helper functions 3: rtm specific
#


def gen_api_sig(param: dict[str, str]) -> str:
    """
    Generate the api_sig.

    according to https://www.rememberthemilk.com/services/api/authentication.rtm
    yxz=foo feg=bar abc=baz
      -> (1. sorting) abc=baz feg=bar yxz=foo
      -> (2.joining) abcbazfegbaryxzfoo -> MD5
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


def rtm_assert_rsp_status_ok(response_text: str) -> None:
    """
    Check that the rest response is ok.

    Must contain <rsp stat="ok">
    """
    if '<rsp stat="ok">' not in response_text:
        msg = f"E: {response_text}"
        raise Exception(msg)  # noqa: TRY002


def rtm_call_method(method: str, arguments: dict[str, str]) -> str:
    """
    Call any rtm API method.

    asserts that the response is ok
    """
    param = {"method": method}
    param.update(arguments)
    param_str = dict_to_url_param(rtm_append_key_and_token_and_sig(param))
    url = f"{URL_RTM_BASE}?{param_str}"
    response_text = perform_rest_call(url)
    rtm_assert_rsp_status_ok(response_text)
    return response_text
