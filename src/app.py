"""Streamlit UI."""

import streamlit as st

from helper import delete_cache

st.set_page_config(page_title="RTM Report", page_icon=None, layout="wide")
st.title("RTM")

delete_cache()
