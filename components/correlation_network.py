import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
import numpy as np
import inspect


def render_network_graph(matrix: pd.DataFrame, threshold: float = 0.3):
    """
    Renders an interactive correlation network graph.
    """

    G = nx.Graph()

    # Add nodes
    for col in matrix.columns:
        G.add_node(col)

    # Add edges
    for i, col1 in enumerate(matrix.columns):
        for j, col2 in enumerate(matrix.columns):
            if i < j:
                corr_val = matrix.iloc[i, j]

                if (
                    not pd.isna(corr_val)
                    and abs(corr_val) >= threshold
                ):
                    G.add_edge(
                        col1,
                        col2,
                        weight=float(corr_val)
                    )

    if G.number_of_edges() == 0:
        st.info(
            "No significant relationships found above the current threshold."
        )
        return

    # Layout
    layout_kwargs = {
        "k": 0.5,
        "iterations": 50
    }

    sig_params = inspect.signature(nx.spring_layout).parameters

    if "seed" in sig_params:
        layout_kwargs["seed"] = 42

    pos = nx.spring_layout(G, **layout_kwargs)

    fig = go.Figure()

    # Edges
    for edge in G.edges(data=True):

        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]

        weight = edge[2]["weight"]

        edge_color = (
            "#22c55e"
            if weight > 0
            else "#ef4444"
        )

        edge_width = 1 + abs(weight) * 5

        fig.add_trace(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode="lines",
                line=dict(
                    width=edge_width,
                    color=edge_color
                ),
                hoverinfo="text",
                text=f"{edge[0]} ↔ {edge[1]}<br>Correlation: {weight:.3f}",
                opacity=0.7,
                showlegend=False
            )
        )

    # Nodes
    node_x = []
    node_y = []
    node_text = []
    node_sizes = []

    degrees = dict(G.degree())

    for node in G.nodes():

        x, y = pos[node]

        node_x.append(x)
        node_y.append(y)

        degree = degrees.get(node, 0)

        node_text.append(
            f"{node}<br>Connections: {degree}"
        )

        node_sizes.append(
            18 + degree * 6
        )

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=list(G.nodes()),
            textposition="top center",
            hovertext=node_text,
            hoverinfo="text",
            marker=dict(
                size=node_sizes,
                color="#1e293b",
                line=dict(
                    width=2,
                    color="#e2e8f0"
                )
            ),
            textfont=dict(
                size=11,
                color="#e2e8f0"
            ),
            showlegend=False
        )
    )

    fig.update_layout(
        title="Feature Relationship Network",
        showlegend=False,
        hovermode="closest",
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )