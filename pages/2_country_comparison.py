import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data

st.set_page_config(page_title="Country Comparison", page_icon="🌍", layout="wide")
st.title("🌍 Country Comparison")

df = load_data()

selected = st.multiselect(
    "Select countries to compare",
    sorted(df["Country"].unique()),
    default=sorted(df["Country"].unique())[:4],
)

if not selected:
    st.info("Select at least one country to see comparisons.")
    st.stop()

subset = df[df["Country"].isin(selected)]

summary = subset.groupby("Country").agg(
    Missions=("Mission Name", "count"),
    Avg_Budget=("Budget (in Billion $)", "mean"),
    Total_Budget=("Budget (in Billion $)", "sum"),
    Avg_Success_Rate=("Success Rate (%)", "mean"),
    Avg_Duration=("Duration (in Days)", "mean"),
).round(2).sort_values("Missions", ascending=False)

st.subheader("Summary Table")
st.dataframe(summary, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    fig = px.bar(
        summary.reset_index(), x="Country", y="Missions",
        title="Mission Count by Country", color="Country"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        summary.reset_index(), x="Country", y="Avg_Budget",
        title="Average Budget per Mission ($B)", color="Country"
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Mission Type Breakdown by Country")
breakdown = (
    subset.groupby(["Country", "Mission Type"]).size()
    .reset_index(name="Count")
)
fig = px.bar(
    breakdown, x="Country", y="Count", color="Mission Type",
    barmode="group", title="Manned vs Unmanned Missions"
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Technology Used by Country")
tech = (
    subset.groupby(["Country", "Technology Used"]).size()
    .reset_index(name="Count")
)
fig = px.bar(
    tech, x="Country", y="Count", color="Technology Used",
    barmode="stack", title="Technology Mix by Country"
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Technology Used by Country (Heatmap)")
tech_country_counts = pd.crosstab(subset["Country"], subset["Technology Used"])
fig = px.imshow(
    tech_country_counts, text_auto=True, color_continuous_scale="YlGnBu",
    labels=dict(color="No. of Missions"),
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Average Mission Duration by Country")
avg_duration = (
    subset.groupby("Country")["Duration (in Days)"].mean()
    .sort_values(ascending=False).reset_index()
)
fig = px.bar(
    avg_duration, x="Country", y="Duration (in Days)", color="Country",
    color_discrete_sequence=px.colors.sequential.Sunset,
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)