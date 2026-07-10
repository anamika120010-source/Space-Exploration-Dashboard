"""
Shared utilities for the Space Exploration Dashboard.
Centralizing data loading here means every page reads the same
cleaned, cached dataframe instead of re-parsing the CSV.
"""
import pandas as pd
import streamlit as st

DATA_PATH = "data/Global_Space_Exploration_Dataset.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and lightly clean the raw dataset. Cached so it only runs once per session."""
    df = pd.read_csv(DATA_PATH)

    # Bucket success rate for easier filtering/coloring elsewhere in the app
    df["Success Tier"] = pd.cut(
        df["Success Rate (%)"],
        bins=[0, 65, 85, 100],
        labels=["Low (<=65%)", "Medium (66-85%)", "High (>85%)"],
    )
    return df


@st.cache_data
def get_collaboration_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Explode the 'Collaborating Countries' comma-separated column into
    one row per (mission country, collaborator) pair. Used for the
    collaboration network / heatmap views.
    """
    rows = []
    for _, row in df.iterrows():
        collaborators = [c.strip() for c in str(row["Collaborating Countries"]).split(",") if c.strip()]
        for collaborator in collaborators:
            if collaborator and collaborator != row["Country"]:
                rows.append({"Country": row["Country"], "Collaborator": collaborator})
    return pd.DataFrame(rows)


def kpi_format_billion(value: float) -> str:
    return f"${value:.2f}B"


@st.cache_data
def get_collab_exploded(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per (mission's Country, individual collaborating country),
    keeping mission-level columns (e.g. Success Rate) intact.
    Mirrors the EDA notebook's df.explode('Collab_list') step.
    """
    d = df.copy()
    d["Collab_list"] = d["Collaborating Countries"].apply(
        lambda x: [c.strip() for c in str(x).split(",")] if pd.notna(x) else []
    )
    return d.explode("Collab_list").reset_index(drop=True)


def get_headline_insights(df: pd.DataFrame) -> dict:
    """Precompute the 'Key Insight' style stats used across the dashboard."""
    top_country = df["Country"].value_counts().idxmax()
    top_country_n = df["Country"].value_counts().max()

    mission_split = df["Mission Type"].value_counts(normalize=True) * 100

    avg_budget_country = df.groupby("Country")["Budget (in Billion $)"].mean().sort_values(ascending=False)

    corr_budget_success = df["Budget (in Billion $)"].corr(df["Success Rate (%)"])
    corr_duration_success = df["Duration (in Days)"].corr(df["Success Rate (%)"])

    missions_per_year = df.groupby("Year").size()
    busiest_year = missions_per_year.idxmax()

    return {
        "top_country": top_country,
        "top_country_n": top_country_n,
        "top_country_pct": top_country_n / len(df) * 100,
        "mission_split_label": (
            f"{mission_split.iloc[0]:.1f}% {mission_split.index[0]} vs "
            f"{mission_split.iloc[1]:.1f}% {mission_split.index[1]}"
        ),
        "highest_budget_country": avg_budget_country.idxmax(),
        "highest_budget_value": avg_budget_country.max(),
        "lowest_budget_country": avg_budget_country.idxmin(),
        "lowest_budget_value": avg_budget_country.min(),
        "corr_budget_success": corr_budget_success,
        "corr_duration_success": corr_duration_success,
        "busiest_year": int(busiest_year),
        "busiest_year_n": int(missions_per_year.max()),
    }