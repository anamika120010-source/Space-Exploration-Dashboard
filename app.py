import streamlit as st
import plotly.express as px
from utils import load_data, kpi_format_billion, get_headline_insights

st.set_page_config(
    page_title="Global Space Exploration Dashboard",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 Global Space Exploration Dashboard")
st.caption(
    "Exploring 3,000 simulated space missions across 10 countries (2000–2025). "
)

df = load_data()
insights = get_headline_insights(df)

# --- KPI row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Missions", f"{len(df):,}")
col2.metric("Countries", df["Country"].nunique())
col3.metric("Total Budget", kpi_format_billion(df["Budget (in Billion $)"].sum()))
col4.metric("Avg Success Rate", f"{df['Success Rate (%)'].mean():.1f}%")

st.divider()

# --- Key insights (mirrors the EDA notebook's printed "Key Insight" lines) ---
st.subheader("Key Insights")
c1, c2 = st.columns(2)
with c1:
    st.info(
        f"**{insights['top_country']}** leads with {insights['top_country_n']} missions "
        f"({insights['top_country_pct']:.1f}% of all missions). Mission split is roughly "
        f"{insights['mission_split_label']} — fairly balanced, no strong tilt toward manned "
        f"or unmanned missions."
    )
    st.info(
        f"**{insights['highest_budget_country']}** has the highest average mission budget "
        f"(${insights['highest_budget_value']:.2f}B), while **{insights['lowest_budget_country']}** "
        f"has the lowest (${insights['lowest_budget_value']:.2f}B)."
    )
with c2:
    st.info(
        f"Correlation between Budget and Success Rate is **{insights['corr_budget_success']:.3f}** "
        "— essentially no linear relationship. Spending more isn't associated with better outcomes "
        "in this dataset, confirming its synthetic/random nature."
    )
    st.info(
        f"**{insights['busiest_year']}** was the busiest year with {insights['busiest_year_n']} missions. "
        f"Duration vs Success Rate correlation is **{insights['corr_duration_success']:.3f}** (negligible)."
    )

st.divider()

# --- Missions by Country & Mission Type ---
st.subheader("Missions by Country and Mission Type")
country_type_counts = (
    df.groupby(["Country", "Mission Type"]).size().reset_index(name="Missions")
)
fig = px.bar(
    country_type_counts, x="Country", y="Missions", color="Mission Type",
    barmode="group", text="Missions",
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig.update_traces(textposition="outside")
fig.update_layout(xaxis_tickangle=-20, yaxis_title="No. of Missions")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Mission Type / Satellite Type / Technology mix ---
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Missions by Type")
    fig = px.bar(
        df["Mission Type"].value_counts().reset_index(),
        x="Mission Type", y="count", color="Mission Type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(showlegend=False, yaxis_title="Missions")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Missions by Satellite Type")
    fig = px.bar(
        df["Satellite Type"].value_counts().reset_index(),
        x="Satellite Type", y="count", color="Satellite Type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(showlegend=False, yaxis_title="Missions")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.subheader("Technology Used")
    fig = px.pie(
        df, names="Technology Used", hole=0.35,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Success Rate Analysis ---
st.subheader("Success Rate Analysis")
c1, c2, c3 = st.columns(3)
with c1:
    fig = px.bar(
        df.groupby("Mission Type")["Success Rate (%)"].mean().reset_index(),
        x="Mission Type", y="Success Rate (%)", color="Mission Type",
        title="Avg Success Rate by Mission Type",
        color_discrete_sequence=["#4C72B0", "#DD8452"],
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    tech_success = (
        df.groupby("Technology Used")["Success Rate (%)"].mean()
        .sort_values(ascending=False).reset_index()
    )
    fig = px.bar(
        tech_success, x="Technology Used", y="Success Rate (%)", color="Technology Used",
        title="Avg Success Rate by Technology",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)

with c3:
    env_success = (
        df.groupby("Environmental Impact")["Success Rate (%)"].mean()
        .reindex(["Low", "Medium", "High"]).reset_index()
    )
    fig = px.bar(
        env_success, x="Environmental Impact", y="Success Rate (%)", color="Environmental Impact",
        title="Avg Success Rate by Environmental Impact",
        color_discrete_sequence=["#55A868", "#DD8452", "#C44E52"],
        category_orders={"Environmental Impact": ["Low", "Medium", "High"]},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("What's in this dashboard")
st.markdown(
    """
- **Explorer** — filter missions by country, year, mission type, and dig into the raw data
- **Country Comparison** — side-by-side stats across countries
- **Trends Over Time** — missions and budget evolution, 2000–2025
- **Collaboration Network** — which countries partner most often, and with whom
"""
)
