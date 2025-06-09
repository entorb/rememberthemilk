"""Streamlit UI."""

from pathlib import Path
from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from streamlit.navigation.page import StreamlitPage

st.set_page_config(page_title="RTM Report", page_icon=None, layout="wide")


def create_navigation_menu() -> None:
    """Create and populate navigation menu."""
    lst: list[StreamlitPage] = []
    for p in sorted(Path("src/reports").glob("*.py")):
        f = p.stem
        t = f[3:].title()
        lst.append(st.Page(page=f"reports/{f}.py", title=t))
    pg = st.navigation(lst)
    pg.run()


create_navigation_menu()

# delete_cache()
