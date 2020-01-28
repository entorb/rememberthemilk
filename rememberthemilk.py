import requests
import hashlib
from configparser import ConfigParser
import re

# by Dr. Torben Menke https://entorb.net

# access to https://www.rememberthemilk.com tasks via their API
# API authentication documentation can be found at https://www.rememberthemilk.com/services/api/authentication.rtm
# list of available API methods can be fount at https://www.rememberthemilk.com/services/api/methods.rtm


config = ConfigParser()
config.read('rememberthemilk.ini')
api_key = config.get('settings', 'api_key')
shared_secret = config.get('settings', 'shared_secret')

url_rtm_base = 'https://api.rememberthemilk.com/services/rest/'

verbose = False  # enable for more logging

#
# helper functions 1: packages
#


def gen_MD5_string(s: str) -> str:
    m = hashlib.md5()
    m.update(s.encode('ascii'))
    return m.hexdigest()


def perform_rest_call(url: str) -> str:
    if verbose == True:
        print("8<-----")
        print(url)
    resp = requests.get(url)
    assert resp.status_code == 200, f'E: bad response. status code:{resp.status_code}, text:\n{resp.text}'
    if verbose == True:
        print(resp.text)
        print("8<-----\n")
    return resp.text


#
# helper functions 2: converters
#

def substr_between(s: str, s1: str, s2: str) -> str:
    """
    returns substring of s, found between strings s1 and s2
    """
    assert s1 in s, f'E: can\'t find \'{s1}\' in \'{s}\''
    assert s2 in s, f'E: can\'t find \'{s1}\' in \'{s}\''
    # TODO: Is a regexp more performant? Check https://pythex.org
    i1 = s.find(s1)+len(s1)
    i2 = s.find(s2)
    assert i1 < i2, f'E: \'{s1}\' not before \'{s2}\' in \'{s}\''
    return s[i1:i2]


def dict2url_param(d: dict) -> str:
    """
    converts a dictionary of parameter: value pairs to an url conform list of key1=value1&key2=value2...
    """
    return "&".join("=".join(tup) for tup in d.items())

#
# helper functions 3: rtm specific
#


def gen_api_sig(param: dict) -> str:
    """
    generates the api_sig according to https://www.rememberthemilk.com/services/api/authentication.rtm
    yxz=foo feg=bar abc=baz -> abc=baz feg=bar yxz=foo -> abcbazfegbaryxzfoo -> MD5
    """
    s = "".join("".join(tup) for tup in sorted(param.items()))
    api_sig = gen_MD5_string(shared_secret + s)
    return api_sig


def rtm_append_key_and_sig(d: dict) -> dict:
    """
    adds api_key (knwon) and api_sig (generated) to dict d
    """
    d['api_key'] = api_key
    d['api_sig'] = gen_api_sig(d)
    return d


def rtm_append_key_and_token_and_sig(d: dict, token: str) -> dict:
    """
    adds api_key (known) auth_token (parameter) and api_sig (generated) to dict d
    """
    d['api_key'] = api_key
    d['auth_token'] = token
    d['api_sig'] = gen_api_sig(d)
    return d


def rtm_assert_rsp_status_ok(reponse_text: str):
    """
    checks a rest response for <rsp stat="ok"> (status = ok)
    """
    assert '<rsp stat="ok">' in reponse_text, 'E: ' + print(reponse_text)


def rtm_call_method(method: str, arguments: dict, token: str) -> str:
    """
    call any rtm API method
    """
    param = {}
    param['method'] = method
    param.update(arguments)
    param_str = dict2url_param(rtm_append_key_and_token_and_sig(param, token))
    url = f'{url_rtm_base}?{param_str}'
    reponse_text = perform_rest_call(url)
    rtm_assert_rsp_status_ok(reponse_text)
    return reponse_text


#
# rtm auth functions
#

def rtm_getFrob():
    """
    ask the API for a frob
    """
    # url = f'https://api.rememberthemilk.com/services/rest/?method=rtm.auth.getFrob&api_key={api_key}&api_sig={api_sig}')
    param = {}
    param['method'] = 'rtm.auth.getFrob'
    param_str = dict2url_param(rtm_append_key_and_sig(param))
    url = f'{url_rtm_base}?{param_str}'
    reponse_text = perform_rest_call(url)
    # <?xml version='1.0' encoding='UTF-8'?><rsp stat="ok"><frob>1a2f3</frob></rsp>
    rtm_assert_rsp_status_ok(reponse_text)
    frob = substr_between(reponse_text, '<frob>', '</frob>')
    return frob


def rtm_gen_auth_url(frob: str) -> str:
    """
    creates a url allowing a user to grant permission on his data to this app
    """
    # https://www.rememberthemilk.com/services/auth/?api_key=abc123&perms=delete&frob=123456&api_sig=zxy987
    url_rtm_auth = 'https://www.rememberthemilk.com/services/auth/'
    param = {}
    param['perms'] = 'read'
    param['frob'] = frob
    param_str = dict2url_param(rtm_append_key_and_sig(param))
    url = f'{url_rtm_auth}?{param_str}'
    return url


def rtm_auth_getToken(frob: str) -> str:
    """
    fetch the user token
    """
    param = {}
    param['method'] = 'rtm.auth.getToken'
    param['frob'] = frob
    param_str = dict2url_param(rtm_append_key_and_sig(param))
    url = f'{url_rtm_base}?{param_str}'
    reponse_text = perform_rest_call(url)
    # <?xml version='1.0' encoding='UTF-8'?><rsp stat="ok"><auth><token>1234</token><perms>read</perms><user id="123" username="myname" fullname="My Full Name"/></auth></rsp>
    rtm_assert_rsp_status_ok(reponse_text)
    token = substr_between(reponse_text, '<token>', '</token>')
    return token

#
# rtm core functions
#


def rtm_lists_getList(token: str) -> str:
    method = 'rtm.lists.getList'
    arguments = {}
    reponse_text = rtm_call_method(method, arguments, token)
    s = substr_between(reponse_text, '<lists>', '</lists>')
    s = s.replace('<list id', "\n<list id")
    # <list id="45663479" name="PC" deleted="0" locked="0" archived="0" position="0" smart="0" sort_order="0"/>
    return s


def rtm_tasks_getList(token: str) -> str:
    method = 'rtm.tasks.getList'
    arguments = {}  # list_id, filter, last_sync = last modified
    # arguments['list_id'] = '45663479' # filter by list ID
    arguments['filter'] = 'CompletedBefore:12/1/2020 completedAfter:31/12/2019'
    arguments['last_sync'] = '2019-12-31'  # filter on last modified date
    reponse_text = rtm_call_method(method, arguments, token)
    s = reponse_text
    # s = substr_between(reponse_text, '<rsp stat="ok">', '</rsp>')
    s = re.sub('^.*<tasks [^>]+>(.*)</tasks>.*$', r'\1', s)

    s = re.sub('<[\w]+/>', '', s)  # remove empty tags
    s = re.sub(' [\w_]+=""', '', s)  # remove empty parameters

    s = re.sub('<notes>.*?</notes>', '', s)  # remove notes
    s = s.replace('has_due_time="0" ', '')  # remove has_due_time

    # add linebreaks
    s = s.replace('</list>', "\n</list>\n\n")
    s = s.replace('<taskseries', "\n<taskseries")

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


# if a token is already available set it here
token = config.get('settings', 'token_entorb')

# here the fun starts...

# print(rtm_lists_getList(token))

print(rtm_tasks_getList(token))
