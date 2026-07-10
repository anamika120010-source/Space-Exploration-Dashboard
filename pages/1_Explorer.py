import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data

st.set_page_config(page_title="Explorer", page_icon="🔍", layout="wide")
st.title("🔍 Mission Explorer")

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filters")

countries = st.sidebar.multiselect(
    "Country", sorted(df["Country"].unique()), default=None
)
mission_types = st.sidebar.multiselect(
    "Mission Type", sorted(df["Mission Type"].unique()), default=None
)
year_range = st.sidebar.slider(
    "Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (int(df["Year"].min()), int(df["Year"].max())),
)

filtered = df.copy()
if countries:
    filtered = filtered[filtered["Country"].isin(countries)]
if mission_types:
    filtered = filtered[filtered["Mission Type"].isin(mission_types)]
filtered = filtered[filtered["Year"].between(*year_range)]

st.caption(f"Showing {len(filtered):,} of {len(df):,} missions")

# --- Charts ---
col1, col2 = st.columns(2)
with col1:
    fig = px.histogram(
        filtered, x="Budget (in Billion $)", nbins=30,
        title="Budget Distribution", color_discrete_sequence=["#636EFA"]
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
        filtered, x="Success Rate (%)", nbins=20,
        title="Success Rate Distribution", color_discrete_sequence=["#EF553B"]
    )
    st.plotly_chart(fig, use_container_width=True)

fig = px.scatter(
    filtered, x="Budget (in Billion $)", y="Success Rate (%)",
    color="Mission Type", hover_data=["Mission Name", "Country", "Year"],
    title="Budget vs Success Rate",
    opacity=0.5,
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Budget Distribution by Satellite Type")
    fig = px.box(
        filtered, x="Satellite Type", y="Budget (in Billion $)", color="Satellite Type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-15)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Environmental Impact by Technology Used")
    tech_impact = pd.crosstab(filtered["Technology Used"], filtered["Environmental Impact"])
    tech_impact = tech_impact.reindex(columns=["Low", "Medium", "High"])
    fig = px.imshow(
        tech_impact, text_auto=True, color_continuous_scale="YlOrRd",
        labels=dict(color="No. of Missions"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Raw data ---
st.subheader("Raw Data")
st.dataframe(filtered, use_container_width=True, height=400)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data as CSV", csv, "filtered_missions.csv", "text/csv")