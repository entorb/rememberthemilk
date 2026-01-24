"""Completed Tasks."""

import altair as alt
import pandas as pd
import streamlit as st

from tasks_completed import completed_week, get_tasks_completed

st.title("Completed")


@st.cache_data(ttl="1h")
def get_df() -> pd.DataFrame:
    """Cache API call."""
    return get_tasks_completed()


df = get_df()
st.dataframe(
    df,
    hide_index=True,
    column_config={"url": st.column_config.LinkColumn("url", display_text="url")},
)

st.header("per Week")
df = completed_week(df)
df = df.reset_index()

sel_param = st.selectbox(
    label="Parameter",
    options=("count", "sum_prio", "sum_overdue_prio", "sum_estimate"),
)

df["completed_week"] = df["completed_week"].astype(str)
chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("completed_week:N", title=None),
        y=alt.Y(f"{sel_param}:Q", title=None),
        color="list:N",
    )
)
st.altair_chart(chart, width="stretch")

st.dataframe(df, hide_index=True)
