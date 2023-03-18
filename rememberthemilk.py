#!/usr/bin/env python3
"""
Using RememberTheMilk API.
"""
import hashlib
import re
from configparser import ConfigParser

import requests

# by Dr. Torben Menke https://entorb.net

# access to https://www.rememberthemilk.com tasks via their API
# API authentication documentation can be found at https://www.rememberthemilk.com/services/api/authentication.rtm
# list of available API methods can be fount at https://www.rememberthemilk.com/services/api/methods.rtm


config = ConfigParser()
config.read("rememberthemilk.ini")
api_key = config.get("settings", "api_key")
shared_secret = config.get("settings", "shared_secret")
token = config.get("settings", "token")

url_rtm_base = "https://api.rememberthemilk.com/services/rest/"

#
# helper functions 1: packages
#


def gen_MD5_string(s: str) -> str:
    m = hashlib.new("md5", usedforsecurity=False)
    m.update(s.encode("ascii"))
    return m.hexdigest()


def perform_rest_call(url: str) -> str:
    resp = requests.get(url, timeout=3)
    assert (
        resp.status_code == 200
    ), f"E: bad response. status code:{resp.status_code}, text:\n{resp.text}"
    return resp.text


#
# helper functions 2: converters
#


def substr_between(s: str, s1: str, s2: str) -> str:
    """
    Return substring of s.

    found between strings s1 and s2
    s1 and s2 can be regular expressions
    """
    myPattern = s1 + "(.*)" + s2
    myRegExp = re.compile(myPattern)
    myMatches = myRegExp.search(s)
    assert myMatches is not None, f"E: can't find '{s1}'...'{s2}' in '{s}'"
    out = myMatches.group(1)
    # Alternative without assert
    # myPattern = '^.*' + s1 + '(.*)' + s2 + '.*$'
    # out = re.sub(myPattern, r'\1', s)
    return out


def dict2url_param(d: dict[str, str]) -> str:
    """
    Convert a dictionary of parameter to string.

    value pairs to an url conform list of key1=value1&key2=value2...
    """
    return "&".join("=".join(tup) for tup in d.items())


#
# helper functions 3: rtm specific
#


def gen_api_sig(param: dict[str, str]) -> str:
    """
    Generate the api_sig.

    according to https://www.rememberthemilk.com/services/api/authentication.rtm
    yxz=foo feg=bar abc=baz -> abc=baz feg=bar yxz=foo -> abcbazfegbaryxzfoo -> MD5
    """
    s = "".join("".join(tup) for tup in sorted(param.items()))
    api_sig = gen_MD5_string(shared_secret + s)
    return api_sig


def rtm_append_key_and_sig(d: dict[str, str]) -> dict[str, str]:
    """
    Add api_key (known) and api_sig (generated) to dict d.
    """
    d["api_key"] = api_key
    d["api_sig"] = gen_api_sig(d)
    return d


def rtm_append_key_and_token_and_sig(d: dict[str, str], token: str) -> dict[str, str]:
    """
    Add api_key (known) auth_token (parameter) and api_sig (generated) to dict d.
    """
    d["api_key"] = api_key
    d["auth_token"] = token
    d["api_sig"] = gen_api_sig(d)
    return d


def rtm_assert_rsp_status_ok(response_text: str) -> None:
    """
    Check a rest response for <rsp stat="ok"> (status = ok).
    """
    assert '<rsp stat="ok">' in response_text, "E: " + response_text


def rtm_call_method(method: str, arguments: dict[str, str], token: str) -> str:
    """
    Call any rtm API method.
    """
    param = {"method": method}
    param.update(arguments)
    param_str = dict2url_param(rtm_append_key_and_token_and_sig(param, token))
    url = f"{url_rtm_base}?{param_str}"
    reponse_text = perform_rest_call(url)
    rtm_assert_rsp_status_ok(reponse_text)
    return reponse_text


#
# rtm auth functions
#


def rtm_getFrob() -> str:
    """
    Ask the API for a frob.
    """
    # url = f'https://api.rememberthemilk.com/services/rest/?method=rtm.auth.getFrob&api_key={api_key}&api_sig={api_sig}') # noqa: E501
    param = {"method": "rtm.auth.getFrob"}
    param_str = dict2url_param(rtm_append_key_and_sig(param))
    url = f"{url_rtm_base}?{param_str}"
    reponse_text = perform_rest_call(url)
    # <?xml version='1.0' encoding='UTF-8'?><rsp stat="ok"><frob>1a2f3</frob></rsp>
    rtm_assert_rsp_status_ok(reponse_text)
    frob = substr_between(reponse_text, "<frob>", "</frob>")
    return frob


def rtm_gen_auth_url(frob: str) -> str:
    """
    Create a url allowing a user to grant permission on his data to this app.
    """
    # https://www.rememberthemilk.com/services/auth/?api_key=abc123&perms=delete&frob=123456&api_sig=zxy987 # noqa: E501
    url_rtm_auth = "https://www.rememberthemilk.com/services/auth/"
    param = {"perms": "read", "frob": frob}
    param_str = dict2url_param(rtm_append_key_and_sig(param))
    url = f"{url_rtm_auth}?{param_str}"
    return url


def rtm_auth_getToken(frob: str) -> str:
    """
    Fetch the user token.
    """
    param = {"method": "rtm.auth.getToken", "frob": frob}
    param_str = dict2url_param(rtm_append_key_and_sig(param))
    url = f"{url_rtm_base}?{param_str}"
    reponse_text = perform_rest_call(url)
    # <?xml version='1.0' encoding='UTF-8'?><rsp stat="ok"><auth><token>1234</token><perms>read</perms><user id="123" username="myname" fullname="My Full Name"/></auth></rsp> # noqa: E501
    rtm_assert_rsp_status_ok(reponse_text)
    token = substr_between(reponse_text, "<token>", "</token>")
    return token


#
# rtm core functions
#


def rtm_lists_getList(token: str) -> str:
    """Fetch lists from RTM."""
    method = "rtm.lists.getList"
    arguments = {}
    reponse_text = rtm_call_method(method, arguments, token)
    s = substr_between(reponse_text, "<lists>", "</lists>")
    s = s.replace("<list id", "\n<list id")
    # <list id="45663479" name="PC" deleted="0" locked="0" archived="0" position="0" smart="0" sort_order="0"/> # noqa: E501

    return s


def rtm_tasks_getList(token: str) -> str:
    """Fetch filtered tasks from RTM."""
    method = "rtm.tasks.getList"
    arguments = {
        "filter": "CompletedBefore:12/1/2030 completedAfter:31/12/2021",
        # "last_sync": "2019-12-31",  # = last modified
    }  # list_id, filter,
    # arguments['list_id'] = '45663479' # filter by list ID
    reponse_text = rtm_call_method(method, arguments, token)
    s = reponse_text
    s = substr_between(s, '<rsp stat="ok">', "</rsp>")
    s = substr_between(s, "<tasks [^>]+>", "</tasks>")
    # s = re.sub('^.*<tasks [^>]+>(.*)</tasks>.*$', r'\1', s)
    s = re.sub(r"<[\w]+/>", "", s)  # remove empty tags
    s = re.sub(r' [\w_]+=""', "", s)  # remove empty parameters

    s = re.sub("<notes>.*?</notes>", "", s)  # remove notes
    s = s.replace('has_due_time="0" ', "")  # remove has_due_time

    # add linebreaks
    s = s.replace("</list>", "\n</list>\n\n")
    s = s.replace("<taskseries", "\n<taskseries")
    return s


#
# perform the auth
#
# this is needed only once: grant this app to access your rtm data
# frob = rtm_getFrob()
# print(f'frob: {frob}')
# print('now open this URL to grant my app access your data:')
# print(rtm_gen_auth_url(frob))
# input("press Enter to continue")
# token = rtm_auth_getToken(frob)
# print(token)


if __name__ == "__main__":
    print("\nRTM Lists")
    print(rtm_lists_getList(token))
    print("\nRTM Tasks")
    print(rtm_tasks_getList(token))
