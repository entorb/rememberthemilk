"""
Playing with RememberTheMilk's API.
"""
import re

# by Dr. Torben Menke https://entorb.net
# access to https://www.rememberthemilk.com tasks via their API
# API authentication documentation can be found at https://www.rememberthemilk.com/services/api/authentication.rtm
# list of available API methods can be fount at https://www.rememberthemilk.com/services/api/methods.rtm
from helper import rtm_call_method, substr_between


def rtm_lists_getList() -> str:  # noqa: N802
    """Fetch lists from RTM."""
    method = "rtm.lists.getList"
    arguments = {}
    s = rtm_call_method(method, arguments)
    s = substr_between(s, "<lists>", "</lists>")

    # add linebreaks
    s = s.replace("<list id", "\n<list id")
    # <list id="45663479" name="PC" deleted="0" locked="0" archived="0" position="0" smart="0" sort_order="0"/> # noqa: E501

    return s


def rtm_tasks_getList() -> str:  # noqa: N802
    """Fetch filtered tasks from RTM."""
    method = "rtm.tasks.getList"
    arguments = {
        "filter": "CompletedBefore:01/01/2999 completedAfter:31/12/2023",
        # "last_sync": "2019-12-31",  # = last modified
    }  # list_id, filter,
    # arguments['list_id'] = '45663479' # filter by list ID
    s = rtm_call_method(method, arguments)
    s = substr_between(s, "<tasks [^>]+>", "</tasks>")
    # s = re.sub('^.*<tasks [^>]+>(.*)</tasks>.*$', r'\1', s)
    s = re.sub(r"<[\w]+/>", "", s)  # remove empty tags
    s = re.sub(r' [\w_]+=""', "", s)  # remove empty parameters

    # remove notes
    s = re.sub("<notes>.*?</notes>", "", s, flags=re.DOTALL)
    s = s.replace('has_due_time="0" ', "")  # remove has_due_time

    # add linebreaks
    s = s.replace("</list>", "\n</list>\n\n")
    s = s.replace("<taskseries", "\n<taskseries")

    return s


if __name__ == "__main__":
    # print("\nRTM Lists")
    # print(rtm_lists_getList())

    print("\nRTM tasks completed this year")
    print(rtm_tasks_getList())
