"""Sprint 4 - Day 25: Sector Analytics Dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import (
    get_home_snapshot,
    get_sectors,
)


# ============================================================
# HELPERS
# ============================================================

def fmt_percent(value):
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


def fmt_number(value):
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:.2f}"


def safe_median(frame, column):
    values = frame[column].dropna()

    if values.empty:
        return None

    return float(values.median())


# ============================================================
# HEADER
# ============================================================

st.title("Sector Analytics")

st.caption(
    "Compare NIFTY 100 companies across the 10 validated "
    "broad sectors using profitability, growth, leverage "
    "and valuation metrics."
)


# ============================================================
# LOAD DATA
# ============================================================

YEAR = "2024-03"

snapshot = get_home_snapshot(
    YEAR
).copy()

sector_master = get_sectors().copy()


# ============================================================
# SECTOR SELECTOR
# ============================================================

sectors = sorted(
    snapshot["broad_sector"]
    .dropna()
    .unique()
    .tolist()
)

selected_sector = st.selectbox(
    "Select sector",
    options=sectors,
)

sector_data = snapshot[
    snapshot["broad_sector"]
    == selected_sector
].copy()


# ============================================================
# SECTOR KPIs
# ============================================================

st.subheader(
    f"{selected_sector} — {YEAR}"
)

company_count = int(
    sector_data["company_id"]
    .nunique()
)

median_roe = safe_median(
    sector_data,
    "roe_pct",
)

median_roce = safe_median(
    sector_data,
    "roce_pct",
)

median_growth = safe_median(
    sector_data,
    "revenue_cagr_5yr",
)

median_pe = safe_median(
    sector_data,
    "pe_ratio",
)

median_de = safe_median(
    sector_data,
    "de_ratio",
)


k1, k2, k3 = st.columns(3)

with k1:
    st.metric(
        "Companies",
        company_count,
    )

with k2:
    st.metric(
        "Median ROE",
        fmt_percent(median_roe),
    )

with k3:
    st.metric(
        "Median ROCE",
        fmt_percent(median_roce),
    )


k4, k5, k6 = st.columns(3)

with k4:
    st.metric(
        "Median Revenue CAGR 5yr",
        fmt_percent(median_growth),
    )

with k5:
    st.metric(
        "Median P/E",
        fmt_number(median_pe),
    )

with k6:
    st.metric(
        "Median D/E",
        fmt_number(median_de),
    )


# ============================================================
# SECTOR UNIVERSE
# ============================================================

st.subheader("Sector Distribution")

sector_counts = (
    snapshot[
        [
            "company_id",
            "broad_sector",
        ]
    ]
    .dropna(
        subset=["broad_sector"]
    )
    .groupby(
        "broad_sector",
        as_index=False,
    )
    .agg(
        Companies=(
            "company_id",
            "nunique",
        )
    )
    .sort_values(
        "Companies",
        ascending=False,
    )
)

distribution_chart = px.bar(
    sector_counts,
    x="broad_sector",
    y="Companies",
    title="NIFTY 100 Companies by Broad Sector",
    labels={
        "broad_sector": "Sector",
    },
)

distribution_chart.update_layout(
    xaxis_tickangle=-35,
)

st.plotly_chart(
    distribution_chart,
    use_container_width=True,
)


# ============================================================
# PROFITABILITY VS GROWTH
# ============================================================

st.subheader(
    "Profitability vs Growth"
)

profit_growth = sector_data.dropna(
    subset=[
        "roe_pct",
        "revenue_cagr_5yr",
    ]
).copy()

if not profit_growth.empty:

    profit_growth_chart = px.scatter(
        profit_growth,
        x="revenue_cagr_5yr",
        y="roe_pct",
        size="market_cap_crore",
        hover_name="company_name",
        hover_data={
            "company_id": True,
            "roce_pct": ":.2f",
            "de_ratio": ":.2f",
            "pe_ratio": ":.2f",
            "market_cap_crore": ":,.0f",
        },
        labels={
            "revenue_cagr_5yr":
                "Revenue CAGR 5yr (%)",
            "roe_pct":
                "ROE (%)",
            "market_cap_crore":
                "Market Cap (₹ Cr)",
            "roce_pct":
                "ROCE (%)",
            "de_ratio":
                "D/E",
            "pe_ratio":
                "P/E",
        },
        title=(
            f"{selected_sector}: "
            "ROE vs Revenue Growth"
        ),
    )

    st.plotly_chart(
        profit_growth_chart,
        use_container_width=True,
    )

else:
    st.info(
        "Insufficient source data for the "
        "profitability-versus-growth chart."
    )


# ============================================================
# COMPANY PROFITABILITY COMPARISON
# ============================================================

st.subheader(
    "Company Profitability Comparison"
)

profitability = sector_data[
    [
        "company_id",
        "company_name",
        "roe_pct",
        "roce_pct",
    ]
].copy()

profitability = profitability.melt(
    id_vars=[
        "company_id",
        "company_name",
    ],
    value_vars=[
        "roe_pct",
        "roce_pct",
    ],
    var_name="Metric",
    value_name="Percent",
)

profitability["Metric"] = (
    profitability["Metric"]
    .replace(
        {
            "roe_pct": "ROE",
            "roce_pct": "ROCE",
        }
    )
)

profitability = profitability.dropna(
    subset=["Percent"]
)

if not profitability.empty:

    profitability_chart = px.bar(
        profitability,
        x="company_id",
        y="Percent",
        color="Metric",
        barmode="group",
        hover_name="company_name",
        labels={
            "company_id": "Ticker",
        },
        title=(
            f"{selected_sector}: "
            "ROE and ROCE"
        ),
    )

    st.plotly_chart(
        profitability_chart,
        use_container_width=True,
    )


# ============================================================
# VALUATION COMPARISON
# ============================================================

st.subheader(
    "Valuation Comparison"
)

valuation = sector_data[
    [
        "company_id",
        "company_name",
        "pe_ratio",
        "pb_ratio",
    ]
].copy()

valuation = valuation.melt(
    id_vars=[
        "company_id",
        "company_name",
    ],
    value_vars=[
        "pe_ratio",
        "pb_ratio",
    ],
    var_name="Metric",
    value_name="Multiple",
)

valuation["Metric"] = (
    valuation["Metric"]
    .replace(
        {
            "pe_ratio": "P/E",
            "pb_ratio": "P/B",
        }
    )
)

valuation = valuation.dropna(
    subset=["Multiple"]
)

if not valuation.empty:

    valuation_chart = px.bar(
        valuation,
        x="company_id",
        y="Multiple",
        color="Metric",
        barmode="group",
        hover_name="company_name",
        labels={
            "company_id": "Ticker",
        },
        title=(
            f"{selected_sector}: "
            "P/E and P/B Multiples"
        ),
    )

    st.plotly_chart(
        valuation_chart,
        use_container_width=True,
    )


# ============================================================
# SECTOR COMPANY TABLE
# ============================================================

st.subheader("Sector Companies")

company_table = sector_data[
    [
        "company_id",
        "company_name",
        "sub_sector",
        "market_cap_category",
        "index_weight_pct",
        "roe_pct",
        "roce_pct",
        "npm_pct",
        "de_ratio",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
    ]
].copy()

company_table = company_table.rename(
    columns={
        "company_id": "Ticker",
        "company_name": "Company",
        "sub_sector": "Sub-Sector",
        "market_cap_category":
            "Market Cap Category",
        "index_weight_pct":
            "Index Weight (%)",
        "roe_pct": "ROE (%)",
        "roce_pct": "ROCE (%)",
        "npm_pct": "NPM (%)",
        "de_ratio": "D/E",
        "revenue_cagr_5yr":
            "Revenue CAGR 5yr (%)",
        "pat_cagr_5yr":
            "PAT CAGR 5yr (%)",
        "market_cap_crore":
            "Market Cap (₹ Cr)",
        "pe_ratio": "P/E",
        "pb_ratio": "P/B",
    }
)

company_table = company_table.sort_values(
    "Market Cap (₹ Cr)",
    ascending=False,
    na_position="last",
)

st.dataframe(
    company_table,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# ALL-SECTOR PERFORMANCE SUMMARY
# ============================================================

st.subheader(
    "All-Sector Financial Summary"
)

sector_summary = (
    snapshot
    .groupby(
        "broad_sector",
        dropna=True,
    )
    .agg(
        Companies=(
            "company_id",
            "nunique",
        ),
        Median_ROE=(
            "roe_pct",
            "median",
        ),
        Median_ROCE=(
            "roce_pct",
            "median",
        ),
        Median_Revenue_CAGR=(
            "revenue_cagr_5yr",
            "median",
        ),
        Median_DE=(
            "de_ratio",
            "median",
        ),
        Median_PE=(
            "pe_ratio",
            "median",
        ),
    )
    .reset_index()
)

sector_summary = sector_summary.rename(
    columns={
        "broad_sector": "Sector",
        "Median_ROE": "Median ROE (%)",
        "Median_ROCE": "Median ROCE (%)",
        "Median_Revenue_CAGR":
            "Median Revenue CAGR 5yr (%)",
        "Median_DE": "Median D/E",
        "Median_PE": "Median P/E",
    }
)

st.dataframe(
    sector_summary,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# SOURCE NOTE
# ============================================================

st.caption(
    "Sector analytics use the validated broad-sector mapping "
    "for all 92 companies and the 2024-03 financial snapshot. "
    "Missing source values are excluded from sector medians "
    "rather than being replaced with zero."
)