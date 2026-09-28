"""Sprint 4 - Day 23: Company Profile."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import (
    get_bs,
    get_cf,
    get_companies,
    get_pl,
    get_ratios,
    get_valuation,
)


# ============================================================
# HELPERS
# ============================================================

def fmt_number(value, decimals=2):
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:,.{decimals}f}"


def fmt_percent(value):
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


def fmt_crore(value):
    if value is None or pd.isna(value):
        return "N/A"

    return f"₹{value:,.0f} Cr"


def latest_row(frame):
    if frame is None or frame.empty:
        return None

    return (
        frame.sort_values(
            "year",
            ascending=False,
        )
        .iloc[0]
    )


# ============================================================
# HEADER
# ============================================================

st.title("Company Profile")

st.caption(
    "Company-level financial statements, ratios, "
    "valuation and historical performance."
)


# ============================================================
# COMPANY SELECTOR
# ============================================================

companies = get_companies().copy()

companies = companies.sort_values(
    "company_name"
)

company_lookup = dict(
    zip(
        companies["company_id"],
        companies["company_name"],
    )
)

company_ids = list(
    company_lookup.keys()
)

default_company = (
    "TCS"
    if "TCS" in company_ids
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
# COMPANY MASTER DATA
# ============================================================

company = companies.loc[
    companies["company_id"]
    == selected_company
].iloc[0]

st.subheader(
    company["company_name"]
)

info1, info2, info3 = st.columns(3)

with info1:
    st.write(
        "**Ticker:**",
        selected_company,
    )

with info2:
    st.write(
        "**Sector:**",
        (
            company["broad_sector"]
            if pd.notna(
                company["broad_sector"]
            )
            else "N/A"
        ),
    )

with info3:
    st.write(
        "**Sub-Sector:**",
        (
            company["sub_sector"]
            if pd.notna(
                company["sub_sector"]
            )
            else "N/A"
        ),
    )


# ============================================================
# LOAD COMPANY DATA
# ============================================================

ratios = get_ratios(
    selected_company
)

pl = get_pl(
    selected_company
)

bs = get_bs(
    selected_company
)

cf = get_cf(
    selected_company
)

valuation = get_valuation(
    selected_company
)

latest_ratios = latest_row(
    ratios
)

latest_pl = latest_row(
    pl
)

latest_bs = latest_row(
    bs
)

latest_cf = latest_row(
    cf
)

latest_valuation = latest_row(
    valuation
)


# ============================================================
# LATEST FINANCIAL PERIOD
# ============================================================

available_periods = []

for frame in [
    ratios,
    pl,
    bs,
    cf,
]:
    if (
        frame is not None
        and not frame.empty
    ):
        available_periods.extend(
            frame["year"]
            .dropna()
            .astype(str)
            .tolist()
        )

if available_periods:
    latest_period = max(
        available_periods
    )

    st.caption(
        f"Latest available financial period: "
        f"{latest_period}"
    )


# ============================================================
# CORE FINANCIAL KPIs
# ============================================================

st.subheader("Latest Financial Snapshot")

k1, k2, k3, k4 = st.columns(4)

with k1:
    value = (
        latest_pl["sales"]
        if latest_pl is not None
        else None
    )

    st.metric(
        "Revenue",
        fmt_crore(value),
    )

with k2:
    value = (
        latest_pl["net_profit"]
        if latest_pl is not None
        else None
    )

    st.metric(
        "Net Profit",
        fmt_crore(value),
    )

with k3:
    value = (
        latest_pl["eps"]
        if latest_pl is not None
        else None
    )

    st.metric(
        "EPS",
        fmt_number(value),
    )

with k4:
    value = (
        latest_valuation[
            "market_cap_crore"
        ]
        if latest_valuation
        is not None
        else None
    )

    st.metric(
        "Market Cap",
        fmt_crore(value),
    )


# ============================================================
# PROFITABILITY AND RETURNS
# ============================================================

st.subheader(
    "Profitability & Returns"
)

r1, r2, r3, r4 = st.columns(4)

with r1:
    value = (
        latest_ratios["roe_pct"]
        if latest_ratios
        is not None
        else None
    )

    st.metric(
        "ROE",
        fmt_percent(value),
    )

with r2:
    value = (
        latest_ratios["roce_pct"]
        if latest_ratios
        is not None
        else None
    )

    st.metric(
        "ROCE",
        fmt_percent(value),
    )

with r3:
    value = (
        latest_ratios["npm_pct"]
        if latest_ratios
        is not None
        else None
    )

    st.metric(
        "Net Profit Margin",
        fmt_percent(value),
    )

with r4:
    value = (
        latest_ratios["de_ratio"]
        if latest_ratios
        is not None
        else None
    )

    st.metric(
        "Debt / Equity",
        fmt_number(value),
    )


# ============================================================
# VALUATION
# ============================================================

st.subheader("Valuation")

v1, v2, v3, v4 = st.columns(4)

with v1:
    value = (
        latest_valuation["pe_ratio"]
        if latest_valuation
        is not None
        else None
    )

    st.metric(
        "P/E",
        fmt_number(value),
    )

with v2:
    value = (
        latest_valuation["pb_ratio"]
        if latest_valuation
        is not None
        else None
    )

    st.metric(
        "P/B",
        fmt_number(value),
    )

with v3:
    value = (
        latest_valuation["ev_ebitda"]
        if latest_valuation
        is not None
        else None
    )

    st.metric(
        "EV / EBITDA",
        fmt_number(value),
    )

with v4:
    value = (
        latest_valuation[
            "dividend_yield_pct"
        ]
        if latest_valuation
        is not None
        else None
    )

    st.metric(
        "Dividend Yield",
        fmt_percent(value),
    )


# ============================================================
# REVENUE & PROFIT TREND
# ============================================================

st.subheader(
    "Revenue & Net Profit Trend"
)

if not pl.empty:

    trend = (
        pl[
            [
                "year",
                "sales",
                "net_profit",
            ]
        ]
        .dropna(
            subset=["year"]
        )
        .sort_values("year")
        .melt(
            id_vars="year",
            value_vars=[
                "sales",
                "net_profit",
            ],
            var_name="Metric",
            value_name="₹ Crore",
        )
    )

    trend["Metric"] = (
        trend["Metric"]
        .replace(
            {
                "sales":
                    "Revenue",
                "net_profit":
                    "Net Profit",
            }
        )
    )

    figure = px.line(
        trend,
        x="year",
        y="₹ Crore",
        color="Metric",
        markers=True,
        title=(
            "Historical Revenue "
            "and Net Profit"
        ),
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )

else:
    st.info(
        "Profit and loss history "
        "is unavailable."
    )


# ============================================================
# FINANCIAL RATIOS HISTORY
# ============================================================

st.subheader(
    "Financial Ratio Trend"
)

if not ratios.empty:

    ratio_trend = (
        ratios[
            [
                "year",
                "roe_pct",
                "roce_pct",
                "npm_pct",
            ]
        ]
        .dropna(
            subset=["year"]
        )
        .sort_values("year")
        .melt(
            id_vars="year",
            value_vars=[
                "roe_pct",
                "roce_pct",
                "npm_pct",
            ],
            var_name="Metric",
            value_name="Percent",
        )
    )

    ratio_trend["Metric"] = (
        ratio_trend["Metric"]
        .replace(
            {
                "roe_pct": "ROE",
                "roce_pct": "ROCE",
                "npm_pct":
                    "Net Profit Margin",
            }
        )
    )

    ratio_figure = px.line(
        ratio_trend,
        x="year",
        y="Percent",
        color="Metric",
        markers=True,
        title=(
            "ROE, ROCE and "
            "Net Profit Margin"
        ),
    )

    st.plotly_chart(
        ratio_figure,
        use_container_width=True,
    )

else:
    st.info(
        "Financial-ratio history "
        "is unavailable."
    )


# ============================================================
# FINANCIAL STATEMENT TABLES
# ============================================================

st.subheader("Financial Statements")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Profit & Loss",
        "Balance Sheet",
        "Cash Flow",
        "Ratios",
    ]
)

with tab1:

    if pl.empty:
        st.info(
            "Profit and loss data unavailable."
        )
    else:
        st.dataframe(
            pl,
            use_container_width=True,
            hide_index=True,
        )


with tab2:

    if bs.empty:
        st.info(
            "Balance-sheet data unavailable."
        )
    else:
        st.dataframe(
            bs,
            use_container_width=True,
            hide_index=True,
        )


with tab3:

    if cf.empty:
        st.info(
            "Cash-flow data unavailable."
        )
    else:
        st.dataframe(
            cf,
            use_container_width=True,
            hide_index=True,
        )


with tab4:

    if ratios.empty:
        st.info(
            "Financial-ratio data unavailable."
        )
    else:
        st.dataframe(
            ratios,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# SOURCE NOTE
# ============================================================

st.caption(
    "Metrics are displayed from the project's SQLite "
    "financial dataset. Different financial statements may "
    "have different latest available periods. Missing source "
    "values are displayed as unavailable rather than being "
    "fabricated."
)