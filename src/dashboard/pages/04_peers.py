"""Sprint 4 - Day 24: Peer Comparison Dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics.peer_comparison import (
    METRIC_LABELS,
    load_peer_comparison_data,
)


# ============================================================
# HEADER
# ============================================================

st.title("Peer Comparison")

st.caption(
    "Compare companies within the 11 validated Sprint 3 "
    "peer groups using raw financial metrics and "
    "peer-relative percentiles."
)


# ============================================================
# LOAD PEER DATA
# ============================================================

raw_rows = load_peer_comparison_data()

columns = [
    "peer_group",
    "company_id",
    "company_name",
    "is_benchmark",
    "year",
    "metric",
    "raw_value",
    "percentile",
]

peer_data = pd.DataFrame(
    raw_rows,
    columns=columns,
)

peer_data["is_benchmark"] = (
    peer_data["is_benchmark"]
    .astype(bool)
)


# ============================================================
# PEER GROUP SELECTOR
# ============================================================

peer_groups = sorted(
    peer_data["peer_group"]
    .dropna()
    .unique()
    .tolist()
)

selected_group = st.selectbox(
    "Select peer group",
    options=peer_groups,
)

group_data = peer_data[
    peer_data["peer_group"]
    == selected_group
].copy()


# ============================================================
# GROUP SUMMARY
# ============================================================

company_count = (
    group_data["company_id"]
    .nunique()
)

benchmark_rows = group_data[
    group_data["is_benchmark"]
]

benchmark_ids = (
    benchmark_rows["company_id"]
    .drop_duplicates()
    .tolist()
)

benchmark_id = (
    benchmark_ids[0]
    if benchmark_ids
    else None
)

benchmark_name = "N/A"

if benchmark_id is not None:
    match = group_data[
        group_data["company_id"]
        == benchmark_id
    ]

    if not match.empty:
        benchmark_name = (
            match.iloc[0][
                "company_name"
            ]
        )


c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Companies",
        company_count,
    )

with c2:
    st.metric(
        "Peer Metrics",
        group_data["metric"].nunique(),
    )

with c3:
    st.metric(
        "Benchmark",
        benchmark_id or "N/A",
    )

st.caption(
    f"Benchmark company: {benchmark_name}"
)


# ============================================================
# COMPANY SELECTOR
# ============================================================

company_table = (
    group_data[
        [
            "company_id",
            "company_name",
        ]
    ]
    .drop_duplicates()
    .sort_values(
        "company_name"
    )
)

company_lookup = dict(
    zip(
        company_table["company_id"],
        company_table["company_name"],
    )
)

company_ids = (
    company_table["company_id"]
    .tolist()
)

default_company = (
    benchmark_id
    if benchmark_id in company_ids
    else company_ids[0]
)

selected_company = st.selectbox(
    "Select company",
    options=company_ids,
    index=company_ids.index(
        default_company
    ),
    format_func=lambda company_id: (
        f"{company_lookup[company_id]} "
        f"({company_id})"
    ),
)


# ============================================================
# COMPANY METRIC TABLE
# ============================================================

company_data = group_data[
    group_data["company_id"]
    == selected_company
].copy()

company_data["Metric"] = (
    company_data["metric"]
    .map(METRIC_LABELS)
    .fillna(
        company_data["metric"]
    )
)

metric_table = company_data[
    [
        "Metric",
        "raw_value",
        "percentile",
    ]
].copy()

metric_table = metric_table.rename(
    columns={
        "raw_value":
            "Raw Value",
        "percentile":
            "Peer Percentile",
    }
)

metric_table = metric_table.sort_values(
    "Peer Percentile",
    ascending=False,
    na_position="last",
)

st.subheader(
    f"{company_lookup[selected_company]} — Peer Metrics"
)

st.dataframe(
    metric_table,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# PERCENTILE BAR CHART
# ============================================================

st.subheader(
    "Peer Percentile Profile"
)

chart_data = metric_table.dropna(
    subset=["Peer Percentile"]
)

if not chart_data.empty:

    percentile_chart = px.bar(
        chart_data,
        x="Peer Percentile",
        y="Metric",
        orientation="h",
        range_x=[0, 100],
        title=(
            f"{selected_company} "
            "Peer Percentiles"
        ),
    )

    percentile_chart.update_layout(
        yaxis={
            "categoryorder":
                "total ascending"
        }
    )

    st.plotly_chart(
        percentile_chart,
        use_container_width=True,
    )

else:
    st.info(
        "No populated peer percentiles "
        "are available for this company."
    )


# ============================================================
# RADAR COMPARISON
# ============================================================

st.subheader(
    "Company vs Benchmark Radar"
)

radar_metrics = [
    "roe_pct",
    "roce_pct",
    "npm_pct",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "cfo_margin_pct",
]

radar_labels = [
    METRIC_LABELS.get(
        metric,
        metric,
    )
    for metric in radar_metrics
]


def percentile_values(
    data,
    company_id,
):
    values = []

    for metric in radar_metrics:

        match = data[
            (data["company_id"] == company_id)
            & (data["metric"] == metric)
        ]

        if match.empty:
            values.append(0.0)
            continue

        value = match.iloc[0][
            "percentile"
        ]

        if pd.isna(value):
            values.append(0.0)
        else:
            values.append(
                float(value)
            )

    return values


company_radar = percentile_values(
    group_data,
    selected_company,
)

benchmark_radar = (
    percentile_values(
        group_data,
        benchmark_id,
    )
    if benchmark_id is not None
    else None
)

radar_figure = go.Figure()

radar_figure.add_trace(
    go.Scatterpolar(
        r=(
            company_radar
            + [company_radar[0]]
        ),
        theta=(
            radar_labels
            + [radar_labels[0]]
        ),
        fill="toself",
        name=selected_company,
    )
)

if (
    benchmark_radar is not None
    and benchmark_id
    != selected_company
):
    radar_figure.add_trace(
        go.Scatterpolar(
            r=(
                benchmark_radar
                + [benchmark_radar[0]]
            ),
            theta=(
                radar_labels
                + [radar_labels[0]]
            ),
            fill="toself",
            name=benchmark_id,
        )
    )

radar_figure.update_layout(
    polar={
        "radialaxis": {
            "visible": True,
            "range": [0, 100],
        }
    },
    showlegend=True,
)

st.plotly_chart(
    radar_figure,
    use_container_width=True,
)


# ============================================================
# FULL PEER GROUP COMPARISON
# ============================================================

st.subheader(
    "Full Peer Group Comparison"
)

selected_metric = st.selectbox(
    "Comparison metric",
    options=sorted(
        group_data["metric"]
        .unique()
        .tolist()
    ),
    format_func=lambda metric: (
        METRIC_LABELS.get(
            metric,
            metric,
        )
    ),
)

comparison = group_data[
    group_data["metric"]
    == selected_metric
][
    [
        "company_id",
        "company_name",
        "is_benchmark",
        "raw_value",
        "percentile",
    ]
].copy()

comparison = comparison.sort_values(
    "percentile",
    ascending=False,
    na_position="last",
)

comparison["Benchmark"] = (
    comparison["is_benchmark"]
    .map(
        {
            True: "Yes",
            False: "No",
        }
    )
)

comparison = comparison.rename(
    columns={
        "company_id":
            "Ticker",
        "company_name":
            "Company",
        "raw_value":
            "Raw Value",
        "percentile":
            "Peer Percentile",
    }
)

comparison = comparison[
    [
        "Ticker",
        "Company",
        "Benchmark",
        "Raw Value",
        "Peer Percentile",
    ]
]

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# SOURCE NOTE
# ============================================================

st.caption(
    "Peer comparisons use the validated Sprint 3 "
    "peer-percentile dataset: 11 peer groups, "
    "56 assigned companies and 15 metrics. "
    "Missing source values remain unavailable rather "
    "than being fabricated."
)