"""Completed Tasks."""  # noqa: INP001

import altair as alt
import streamlit as st

from tasks_overdue import get_tasks_overdue, group_by_list

st.set_page_config(page_title="RTM Overdue", page_icon=None, layout="wide")
st.title("Overdue")

df = get_tasks_overdue().sort_values(by=["overdue"], ascending=[True])
lists = sorted(set(df["list"].to_list()))

sel_list = st.selectbox(label="List", index=None, options=lists)

st.dataframe(
    df.query(f"list == '{sel_list}'") if sel_list else df,
    hide_index=True,
    column_config={"url": st.column_config.LinkColumn("url", display_text="url")},
)

st.header("by List")
df = group_by_list(df)
df = df.reset_index()


sel_list = st.selectbox(
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
st.altair_chart(chart, use_container_width=True)

st.dataframe(df, hide_index=True)
