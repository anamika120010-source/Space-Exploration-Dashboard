# 🚀 Global Space Exploration Dashboard

An interactive Streamlit dashboard exploring 3,000 simulated space missions
across 10 countries (2000–2025).

## Data note

This dataset is **synthetically generated** (not real mission records) —
generated for practicing data exploration, filtering, and visualization at
scale. During EDA I checked for statistical relationships between features
(budget, technology, country, etc.) and outcomes (success rate) and found
none — confirming the data has no real predictive signal. Because of that,
this project focuses on exploratory analysis and visualization rather than
predictive modeling, which wouldn't be a genuine fit for this data.

## Setup

\`\`\`bash
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
\`\`\`

## Pages

- **Home** — key metrics and dataset overview
- **Explorer** — filter missions by country/year/type; budget & success rate distributions
- **Country Comparison** — side-by-side stats across selected countries
- **Trends Over Time** — mission volume, budget, and technology mix by year
- **Collaboration Network** — parses the `Collaborating Countries` field into a
  heatmap and network graph of which countries partner most often

## Tech stack

Python, pandas, Streamlit, Plotly, NetworkX