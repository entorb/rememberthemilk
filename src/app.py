"""Streamlit UI."""

from pathlib import Path

import streamlit as st

st.set_page_config(page_title="RTM Report", page_icon=None, layout="wide")


def create_navigation_menu() -> None:
    """Create and populate navigation menu."""
    lst = []
    for p in sorted(Path("src/reports").glob("*.py")):
        f = p.stem
        t = f[3:].title()
        lst.append(st.Page(page=f"reports/{f}.py", title=t))
    pg = st.navigation(lst)
    pg.run()


create_navigation_menu()

# delete_cache()
