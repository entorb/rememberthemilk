"""Completed Tasks."""

import altair as alt
import pandas as pd
import streamlit as st

from tasks_overdue import get_tasks_overdue, group_by_list

st.title("Overdue")


@st.cache_data(ttl="1h")
def get_df() -> pd.DataFrame:
    """Cache API call."""
    return get_tasks_overdue().sort_values(by=["overdue"], ascending=[True])


df = get_df()
lists = sorted(set(df["list"].to_list()))

col1, _ = st.columns((1, 5))
sel_list = col1.selectbox(label="List", index=None, options=lists)

st.dataframe(
    df.query(f"list == '{sel_list}'") if sel_list else df,
    hide_index=True,
    column_config={"url": st.column_config.LinkColumn("url", display_text="url")},
)

st.header("by List")
df = group_by_list(df)
df = df.reset_index()


col1, _ = st.columns((1, 5))
sel_list = col1.selectbox(
    label="Parameter",
    options=("count", "sum_prio", "sum_overdue_prio", "sum_estimate"),
)

chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("list:N", title=None),
        y=alt.Y(f"{sel_list}:Q", title=None),
        color="list:N",
    )
)
st.altair_chart(chart, width="stretch")

st.dataframe(df, hide_index=True)
