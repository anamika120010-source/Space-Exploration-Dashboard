import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data

st.set_page_config(page_title="Trends Over Time", page_icon="📈", layout="wide")
st.title("📈 Trends Over Time (2000–2025)")

df = load_data()

by_year = df.groupby("Year").agg(
    Missions=("Mission Name", "count"),
    Total_Budget=("Budget (in Billion $)", "sum"),
    Avg_Success_Rate=("Success Rate (%)", "mean"),
).reset_index()
by_year["Rolling_3yr"] = by_year["Missions"].rolling(3, center=True).mean()

busiest_year = int(by_year.loc[by_year["Missions"].idxmax(), "Year"])
busiest_year_n = int(by_year["Missions"].max())
trend_corr = np.corrcoef(by_year["Year"], by_year["Missions"])[0, 1]
trend_label = "a rising trend" if trend_corr > 0.2 else ("a declining trend" if trend_corr < -0.2 else "no strong trend")

st.info(
    f"**{busiest_year}** was the busiest year with {busiest_year_n} missions. "
    f"Year-over-year mission count shows **{trend_label}** over {int(df['Year'].min())}–{int(df['Year'].max())} "
    f"(correlation with year: {trend_corr:.2f})."
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Missions per Year (with 3-Year Rolling Average)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=by_year["Year"], y=by_year["Missions"], mode="lines+markers",
        name="Missions per year",
    ))
    fig.add_trace(go.Scatter(
        x=by_year["Year"], y=by_year["Rolling_3yr"], mode="lines",
        name="3-year rolling average", line=dict(dash="dash", color="red"),
    ))
    fig.update_layout(xaxis_title="Year", yaxis_title="Number of Missions")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.line(by_year, x="Year", y="Total_Budget", markers=True, title="Total Budget per Year ($B)")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Missions per Year by Country")
by_year_country = df.groupby(["Year", "Country"]).size().reset_index(name="Missions")
fig = px.line(
    by_year_country, x="Year", y="Missions", color="Country",
    title="Country Activity Over Time"
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Technology Adoption Over Time")
tech_year = df.groupby(["Year", "Technology Used"]).size().reset_index(name="Count")
fig = px.area(
    tech_year, x="Year", y="Count", color="Technology Used",
    title="Technology Mix Over Time"
)
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Note: earlier EDA showed no significant correlation between Year and Success Rate "
    "or Budget — trends here reflect volume/mix shifts, not performance improvements."
)