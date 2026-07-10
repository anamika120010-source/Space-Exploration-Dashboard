import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from utils import load_data, get_collaboration_pairs, get_collab_exploded

st.set_page_config(page_title="Collaboration Network", page_icon="🤝", layout="wide")
st.title("🤝 International Collaboration Network")

df = load_data()
pairs = get_collaboration_pairs(df)

st.caption(
    f"Parsed {len(pairs):,} country-pair collaborations from the "
    "'Collaborating Countries' field."
)

# --- Heatmap of collaboration counts ---
st.subheader("Collaboration Frequency Heatmap")
matrix = pairs.groupby(["Country", "Collaborator"]).size().unstack(fill_value=0)
fig = px.imshow(
    matrix, color_continuous_scale="Blues", text_auto=True,
    title="How often each country pair collaborates",
    labels=dict(color="Collaborations"),
)
st.plotly_chart(fig, use_container_width=True)

# --- Average success rate by collaborating pair ---
st.subheader("Average Success Rate by Collaborating Country Pair")
exploded = get_collab_exploded(df)
exploded = exploded[exploded["Collab_list"] != ""]
success_matrix = exploded.pivot_table(
    index="Country", columns="Collab_list", values="Success Rate (%)", aggfunc="mean"
)
fig = px.imshow(
    success_matrix, text_auto=".1f", color_continuous_scale="RdYlGn",
    labels=dict(color="Avg Success Rate (%)"),
)
st.plotly_chart(fig, use_container_width=True)

# --- Top collaborating pairs ---
st.subheader("Top Collaborating Pairs")
pair_counts = (
    pairs.assign(pair=pairs.apply(lambda r: tuple(sorted([r["Country"], r["Collaborator"]])), axis=1))
    .groupby("pair").size().reset_index(name="Count")
    .sort_values("Count", ascending=False)
    .head(10)
)
pair_counts["Pair"] = pair_counts["pair"].apply(lambda p: f"{p[0]} ↔ {p[1]}")
fig = px.bar(pair_counts, x="Count", y="Pair", orientation="h", title="Top 10 Country Pairs")
fig.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

# --- Network graph ---
st.subheader("Network Graph")
st.caption("Node size reflects number of missions; edge thickness reflects collaboration count.")

G = nx.Graph()
mission_counts = df["Country"].value_counts()
for country, count in mission_counts.items():
    G.add_node(country, missions=count)

edge_weights = pairs.groupby(["Country", "Collaborator"]).size().reset_index(name="weight")
for _, row in edge_weights.iterrows():
    a, b, w = row["Country"], row["Collaborator"], row["weight"]
    if G.has_edge(a, b):
        G[a][b]["weight"] += w
    else:
        G.add_edge(a, b, weight=w)

pos = nx.spring_layout(G, seed=42, k=0.8)

edge_x, edge_y = [], []
for u, v in G.edges():
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scatter(
    x=edge_x, y=edge_y, mode="lines",
    line=dict(width=1, color="#888"), hoverinfo="none"
)

node_x = [pos[n][0] for n in G.nodes()]
node_y = [pos[n][1] for n in G.nodes()]
node_size = [G.nodes[n]["missions"] / 5 for n in G.nodes()]
node_text = [f"{n}: {G.nodes[n]['missions']} missions" for n in G.nodes()]

node_trace = go.Scatter(
    x=node_x, y=node_y, mode="markers+text",
    text=list(G.nodes()), textposition="top center",
    hovertext=node_text, hoverinfo="text",
    marker=dict(size=node_size, color="#636EFA", line=dict(width=1, color="white")),
)

fig = go.Figure(data=[edge_trace, node_trace])
fig.update_layout(
    showlegend=False, height=600,
    xaxis=dict(showgrid=False, zeroline=False, visible=False),
    yaxis=dict(showgrid=False, zeroline=False, visible=False),
    title="Country Collaboration Network",
)
st.plotly_chart(fig, use_container_width=True)