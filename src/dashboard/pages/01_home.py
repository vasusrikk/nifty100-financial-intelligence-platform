"""Sprint 4 - Day 23: NIFTY 100 Home Dashboard."""

from __future__ import annotations

import plotly.express as px
import streamlit as st
from src.screener.scoring import rank_companies

from src.dashboard.utils.db import (
    get_available_ratio_years,
    get_home_snapshot,
    get_home_summary,
)


# ============================================================
# HELPERS
# ============================================================

def format_percent(value):
    if value is None:
        return "N/A"

    return f"{value:.2f}%"


def format_number(value):
    if value is None:
        return "N/A"

    return f"{value:.2f}"


# ============================================================
# HEADER
# ============================================================

st.title("NIFTY 100 Analytics")

st.caption(
    "Financial intelligence dashboard for screening, "
    "peer comparison, trends, sectors and valuation."
)


# ============================================================
# PERIOD SELECTOR
# ============================================================

year_data = get_available_ratio_years()

required_years = [
    "2019-03",
    "2020-03",
    "2021-03",
    "2022-03",
    "2023-03",
    "2024-03",
]

available_years = set(
    year_data["year"].astype(str)
)

years = [
    year
    for year in required_years
    if year in available_years
]

default_year = (
    "2024-03"
    if "2024-03" in years
    else years[-1]
)
selected_year = st.selectbox(
    "Financial period",
    options=years,
    index=years.index(
        default_year
    ),
)

snapshot = get_home_snapshot(
    selected_year
)

summary = get_home_summary(
    selected_year
)


# ============================================================
# REQUIRED HOME KPI CARDS
# ============================================================

st.subheader(
    f"Market Overview — {selected_year}"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average ROE",
        format_percent(
            summary["average_roe"]
        ),
    )

with col2:
    st.metric(
        "Median P/E",
        format_number(
            summary["median_pe"]
        ),
    )

with col3:
    st.metric(
        "Median D/E",
        format_number(
            summary["median_de"]
        ),
    )


col4, col5, col6 = st.columns(3)

with col4:
    st.metric(
        "Total Companies",
        summary["total_companies"],
    )

with col5:
    st.metric(
        "Median Revenue CAGR 5yr",
        format_percent(
            summary[
                "median_revenue_cagr_5yr"
            ]
        ),
    )

with col6:
    st.metric(
        "Debt-Free Companies",
        summary[
            "debt_free_companies"
        ],
    )






# ============================================================
# DATA COVERAGE
# ============================================================

st.subheader("Data Coverage")

coverage1, coverage2 = st.columns(2)

with coverage1:
    st.metric(
        "Financial Ratios",
        (
            f'{summary["ratio_coverage"]}'
            f' / {summary["total_companies"]}'
        ),
    )

with coverage2:
    st.metric(
        "Market Capitalisation",
        (
            f'{summary["market_cap_coverage"]}'
            f' / {summary["total_companies"]}'
        ),
    )

if (
    summary["ratio_coverage"]
    < summary["total_companies"]
):
    st.info(
        "Financial-ratio coverage is incomplete for this "
        "period. Missing source values remain unavailable "
        "rather than being treated as zero."
    )




# ============================================================
# SECTOR BREAKDOWN DONUT CHART
# ============================================================

st.subheader("Sector Breakdown")

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
        companies=(
            "company_id",
            "nunique",
        )
    )
    .sort_values(
        "companies",
        ascending=False,
    )
)

sector_chart = px.pie(
    sector_counts,
    names="broad_sector",
    values="companies",
    hole=0.48,
    title="NIFTY 100 Sector Breakdown",
)

sector_chart.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Companies: %{value}<br>"
        "Share: %{percent}"
        "<extra></extra>"
    ),
)

sector_chart.update_layout(
    legend_title_text="Sector",
)

st.plotly_chart(
    sector_chart,
    use_container_width=True,
)

# ============================================================
# PROFITABILITY VS LEVERAGE
# ============================================================

st.subheader(
    "Profitability vs Leverage"
)

scatter_data = snapshot.dropna(
    subset=[
        "roe_pct",
        "de_ratio",
    ]
).copy()

if not scatter_data.empty:

    scatter_chart = px.scatter(
        scatter_data,
        x="de_ratio",
        y="roe_pct",
        color="broad_sector",
        hover_name="company_name",
        hover_data={
            "company_id": True,
            "roce_pct": ":.2f",
            "revenue_cagr_5yr": ":.2f",
            "de_ratio": ":.2f",
            "roe_pct": ":.2f",
        },
        labels={
            "de_ratio":
                "Debt / Equity",
            "roe_pct":
                "ROE (%)",
            "broad_sector":
                "Sector",
            "roce_pct":
                "ROCE (%)",
            "revenue_cagr_5yr":
                "Revenue CAGR (%)",
        },
        title=(
            "ROE vs Debt / Equity"
        ),
    )

    st.plotly_chart(
        scatter_chart,
        use_container_width=True,
    )

else:
    st.warning(
        "Insufficient source data for "
        "profitability-versus-leverage analysis."
    )


# ============================================================
# MARKET-CAP LEADERS
# ============================================================

st.subheader("Largest Companies")

market_leaders = (
    snapshot.dropna(
        subset=[
            "market_cap_crore"
        ]
    )
    .nlargest(
        10,
        "market_cap_crore",
    )
    [
        [
            "company_id",
            "company_name",
            "broad_sector",
            "market_cap_crore",
            "pe_ratio",
            "roe_pct",
            "roce_pct",
        ]
    ]
    .copy()
)

market_leaders = (
    market_leaders.rename(
        columns={
            "company_id":
                "Ticker",
            "company_name":
                "Company",
            "broad_sector":
                "Sector",
            "market_cap_crore":
                "Market Cap (₹ Cr)",
            "pe_ratio":
                "P/E",
            "roe_pct":
                "ROE (%)",
            "roce_pct":
                "ROCE (%)",
        }
    )
)

st.dataframe(
    market_leaders,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# SNAPSHOT TABLE
# ============================================================

with st.expander(
    "View complete company snapshot"
):

    display = snapshot[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "sub_sector",
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

    display = display.rename(
        columns={
            "company_id":
                "Ticker",
            "company_name":
                "Company",
            "broad_sector":
                "Sector",
            "sub_sector":
                "Sub-Sector",
            "roe_pct":
                "ROE (%)",
            "roce_pct":
                "ROCE (%)",
            "npm_pct":
                "NPM (%)",
            "de_ratio":
                "D/E",
            "revenue_cagr_5yr":
                "Revenue CAGR (%)",
            "pat_cagr_5yr":
                "PAT CAGR (%)",
            "market_cap_crore":
                "Market Cap (₹ Cr)",
            "pe_ratio":
                "P/E",
            "pb_ratio":
                "P/B",
        }
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )



# ============================================================
# TOP 5 COMPOSITE QUALITY SCORES
# ============================================================

st.subheader("Top 5 Companies by Composite Quality Score")

ranked_companies = rank_companies()

top_five = ranked_companies[:5]

top_five_rows = []

for rank, company in enumerate(
    top_five,
    start=1,
):
    top_five_rows.append(
        {
            "Rank": rank,
            "Ticker": company.get(
                "company_id"
            ),
            "Company": company.get(
                "company_name"
            ),
            "Composite Score": company.get(
                "composite_score"
            ),
            "Score Coverage (%)": company.get(
                "score_coverage_pct"
            ),
        }
    )

st.dataframe(
    top_five_rows,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Composite scores use the existing Sprint 3 "
    "scoring and ranking engine. Score coverage shows "
    "the percentage of configured scoring weight supported "
    "by available source metrics."
)




# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Source: project SQLite financial dataset. "
    "Unavailable source metrics are displayed as missing "
    "and are not automatically converted to zero."
)