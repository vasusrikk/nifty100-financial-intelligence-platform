"""Sprint 4 - Day 23: Company Profile."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.dashboard.utils.db import (
    get_bs,
    get_cf,
    get_companies,
    get_generated_pros_cons,
    get_pl,
    get_ratios,
    get_valuation,
)


# ============================================================
# HELPERS
# ============================================================

def fmt_number(value, decimals=2):
    """Format a numeric value or return N/A."""

    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:,.{decimals}f}"


def fmt_percent(value):
    """Format a percentage value or return N/A."""

    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


def fmt_crore(value):
    """Format a rupee-crore value or return N/A."""

    if value is None or pd.isna(value):
        return "N/A"

    return f"₹{value:,.0f} Cr"


def latest_row(frame):
    """Return the latest row by financial year."""

    if frame is None or frame.empty:
        return None

    return (
        frame
        .sort_values(
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
# COMPANY SEARCH / SELECTOR
# ============================================================

companies = get_companies().copy()

if companies.empty:
    st.error(
        "Company master data is unavailable."
    )
    st.stop()


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
    "Search / Select Company",
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
# COMPANY CARD
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

generated_insights = get_generated_pros_cons(
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
# LATEST AVAILABLE PERIOD
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
        and "year" in frame.columns
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
        "Latest available financial period: "
        f"{latest_period}"
    )


# ============================================================
# REQUIRED SIX KPI TILES
# ============================================================

st.subheader(
    "Key Financial Metrics"
)

k1, k2, k3 = st.columns(3)

with k1:

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


with k2:

    value = (
        latest_valuation[
            "pe_ratio"
        ]
        if latest_valuation
        is not None
        else None
    )

    st.metric(
        "P/E",
        fmt_number(value),
    )


with k3:

    value = (
        latest_ratios[
            "roe_pct"
        ]
        if latest_ratios
        is not None
        else None
    )

    st.metric(
        "ROE",
        fmt_percent(value),
    )


k4, k5, k6 = st.columns(3)

with k4:

    value = (
        latest_ratios[
            "roce_pct"
        ]
        if latest_ratios
        is not None
        else None
    )

    st.metric(
        "ROCE",
        fmt_percent(value),
    )


with k5:

    value = (
        latest_ratios[
            "de_ratio"
        ]
        if latest_ratios
        is not None
        else None
    )

    st.metric(
        "D/E",
        fmt_number(value),
    )


with k6:

    value = (
        latest_ratios[
            "revenue_cagr_5yr"
        ]
        if latest_ratios
        is not None
        else None
    )

    st.metric(
        "Revenue CAGR 5yr",
        fmt_percent(value),
    )


# ============================================================
# 10-YEAR REVENUE + NET PROFIT BAR CHART
# ============================================================

st.subheader(
    "10-Year Revenue & Net Profit"
)

if (
    pl is not None
    and not pl.empty
):

    pl_trend = (
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
        .tail(10)
        .copy()
    )

    if not pl_trend.empty:

        pl_long = pl_trend.melt(
            id_vars="year",
            value_vars=[
                "sales",
                "net_profit",
            ],
            var_name="Metric",
            value_name="Value",
        )

        pl_long["Metric"] = (
            pl_long["Metric"]
            .replace(
                {
                    "sales":
                        "Revenue",
                    "net_profit":
                        "Net Profit",
                }
            )
        )

        profit_figure = px.bar(
            pl_long,
            x="year",
            y="Value",
            color="Metric",
            barmode="group",
            labels={
                "year":
                    "Financial Period",
                "Value":
                    "₹ Crore",
            },
            title=(
                "Revenue and Net Profit "
                "- Latest 10 Available Years"
            ),
        )

        profit_figure.update_layout(
            xaxis_title=(
                "Financial Period"
            ),
            yaxis_title="₹ Crore",
            legend_title="Metric",
        )

        st.plotly_chart(
            profit_figure,
            use_container_width=True,
        )

    else:

        st.info(
            "Revenue and net-profit "
            "history is unavailable."
        )

else:

    st.info(
        "Revenue and net-profit "
        "history is unavailable."
    )


# ============================================================
# 10-YEAR ROE + ROCE DUAL-AXIS CHART
# ============================================================

st.subheader(
    "10-Year ROE & ROCE Trend"
)

if (
    ratios is not None
    and not ratios.empty
):

    return_trend = (
        ratios[
            [
                "year",
                "roe_pct",
                "roce_pct",
            ]
        ]
        .dropna(
            subset=["year"]
        )
        .sort_values("year")
        .tail(10)
        .copy()
    )

    if not return_trend.empty:

        return_figure = go.Figure()

        return_figure.add_trace(
            go.Scatter(
                x=(
                    return_trend[
                        "year"
                    ]
                ),
                y=(
                    return_trend[
                        "roe_pct"
                    ]
                ),
                name="ROE",
                mode="lines+markers",
                yaxis="y",
            )
        )

        return_figure.add_trace(
            go.Scatter(
                x=(
                    return_trend[
                        "year"
                    ]
                ),
                y=(
                    return_trend[
                        "roce_pct"
                    ]
                ),
                name="ROCE",
                mode="lines+markers",
                yaxis="y2",
            )
        )

        return_figure.update_layout(
            title=(
                "ROE and ROCE "
                "- Latest 10 Available Years"
            ),
            xaxis=dict(
                title=(
                    "Financial Period"
                )
            ),
            yaxis=dict(
                title="ROE (%)",
            ),
            yaxis2=dict(
                title="ROCE (%)",
                overlaying="y",
                side="right",
            ),
            legend=dict(
                orientation="h",
            ),
        )

        st.plotly_chart(
            return_figure,
            use_container_width=True,
        )

    else:

        st.info(
            "ROE and ROCE history "
            "is unavailable."
        )

else:

    st.info(
        "ROE and ROCE history "
        "is unavailable."
    )


# ============================================================
# NLP-GENERATED PROS & CONS
# ============================================================

st.subheader("Pros & Cons")

st.caption(
    "Rule-based financial insights generated from the "
    "structured Sprint 5 analysis data."
)

pros = pd.DataFrame()
cons = pd.DataFrame()

if (
    generated_insights is not None
    and not generated_insights.empty
):

    pros = generated_insights[
        generated_insights["signal_type"] == "PRO"
    ].copy()

    cons = generated_insights[
        generated_insights["signal_type"] == "CON"
    ].copy()


pros_col, cons_col = st.columns(2)


with pros_col:

    st.markdown("### Pros")

    if not pros.empty:

        for _, insight in pros.iterrows():

            message = insight["message"]
            period = insight["period"]
            metric = insight["metric"]

            st.success(
                f"✓ {message}\n\n"
                f"**{metric} · {period}**"
            )

    else:

        st.info(
            "No positive signals were generated "
            "for this company."
        )


with cons_col:

    st.markdown("### Cons")

    if not cons.empty:

        for _, insight in cons.iterrows():

            message = insight["message"]
            period = insight["period"]
            metric = insight["metric"]

            st.error(
                f"✗ {message}\n\n"
                f"**{metric} · {period}**"
            )

    else:

        st.info(
            "No negative signals were generated "
            "for this company."
        )


if (
    generated_insights is None
    or generated_insights.empty
):

    st.caption(
        "Generated Sprint 5 analysis is currently "
        "unavailable for this company."
    )


# ============================================================
# FINANCIAL STATEMENT TABLES
# ============================================================

st.subheader(
    "Financial Statements"
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Profit & Loss",
        "Balance Sheet",
        "Cash Flow",
        "Ratios",
    ]
)


with tab1:

    if (
        pl is None
        or pl.empty
    ):

        st.info(
            "Profit and loss "
            "data unavailable."
        )

    else:

        st.dataframe(
            pl,
            use_container_width=True,
            hide_index=True,
        )


with tab2:

    if (
        bs is None
        or bs.empty
    ):

        st.info(
            "Balance-sheet "
            "data unavailable."
        )

    else:

        st.dataframe(
            bs,
            use_container_width=True,
            hide_index=True,
        )


with tab3:

    if (
        cf is None
        or cf.empty
    ):

        st.info(
            "Cash-flow data "
            "unavailable."
        )

    else:

        st.dataframe(
            cf,
            use_container_width=True,
            hide_index=True,
        )


with tab4:

    if (
        ratios is None
        or ratios.empty
    ):

        st.info(
            "Financial-ratio "
            "data unavailable."
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
    "Financial metrics are displayed from the project's "
    "SQLite dataset. The charts use up to the latest 10 "
    "available financial periods. Missing source values are "
    "displayed as N/A rather than being fabricated."
)