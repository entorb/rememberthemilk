"""
Authentication for RememberTheMilk API.

Only needed once.
"""

from helper import (
    URL_RTM_BASE,
    dict_to_url_param,
    perform_rest_call,
    rtm_append_key_and_sig,
    rtm_assert_rsp_status_ok,
    substr_between,
)


def rtm_get_frob() -> str:
    """
    Ask the API for a frob.
    """
    # url = f'https://api.rememberthemilk.com/services/rest/?method=rtm.auth.getFrob&api_key={api_key}&api_sig={api_sig}') # noqa: E501
    param = {"method": "rtm.auth.getFrob"}
    param_str = dict_to_url_param(rtm_append_key_and_sig(param))
    url = f"{URL_RTM_BASE}?{param_str}"
    response_text = perform_rest_call(url)
    # <?xml version='1.0' encoding='UTF-8'?><rsp stat="ok"><frob>1a2f3</frob></rsp>
    rtm_assert_rsp_status_ok(response_text)
    frob = substr_between(response_text, "<frob>", "</frob>")
    return frob


def rtm_gen_auth_url(frob: str) -> str:
    """
    Create a url allowing a user to grant permission on his data to this app.
    """
    # https://www.rememberthemilk.com/services/auth/?api_key=abc123&perms=delete&frob=123456&api_sig=zxy987 # noqa: E501
    url_rtm_auth = "https://www.rememberthemilk.com/services/auth/"
    param = {"perms": "read", "frob": frob}
    param_str = dict_to_url_param(rtm_append_key_and_sig(param))
    url = f"{url_rtm_auth}?{param_str}"
    return url


def rtm_auth_get_token(frob: str) -> str:
    """
    Fetch the user token.
    """
    param = {"method": "rtm.auth.getToken", "frob": frob}
    param_str = dict_to_url_param(rtm_append_key_and_sig(param))
    url = f"{URL_RTM_BASE}?{param_str}"
    response_text = perform_rest_call(url)
    # <?xml version='1.0' encoding='UTF-8'?><rsp stat="ok"><auth><token>1234</token><perms>read</perms><user id="123" username="username" fullname="My Full Name"/></auth></rsp> # noqa: E501
    rtm_assert_rsp_status_ok(response_text)
    token = substr_between(response_text, "<token>", "</token>")
    return token


def auth() -> None:
    """
    Perform the authentication.

    Only needed once.
    """
    frob = rtm_get_frob()
    print(f"frob: {frob}")
    print("now open this URL to grant this app access your data:")
    print(rtm_gen_auth_url(frob))
    input("press Enter to continue")
    token = rtm_auth_get_token(frob)
    print(token)


if __name__ == "__main__":
    auth()
