"""Sprint 4 - Day 26: Capital Allocation Dashboard."""

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
)


# ============================================================
# HELPERS
# ============================================================

def fmt_number(value):
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:,.2f}"


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

st.title("Capital Allocation")

st.caption(
    "Analyze how companies generate, deploy and finance "
    "capital using cash-flow, balance-sheet and capital-"
    "efficiency metrics."
)


# ============================================================
# COMPANY SELECTOR
# ============================================================

companies = (
    get_companies()
    .sort_values("company_name")
    .copy()
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
# LOAD DATA
# ============================================================

cashflow = get_cf(
    selected_company
).copy()

ratios = get_ratios(
    selected_company
).copy()

balance_sheet = get_bs(
    selected_company
).copy()

profit_loss = get_pl(
    selected_company
).copy()

latest_cf = latest_row(cashflow)
latest_ratios = latest_row(ratios)
latest_bs = latest_row(balance_sheet)
latest_pl = latest_row(profit_loss)


# ============================================================
# CAPITAL EFFICIENCY KPIs
# ============================================================

st.subheader("Capital Efficiency")

k1, k2, k3, k4 = st.columns(4)

with k1:
    value = (
        latest_ratios["roce_pct"]
        if latest_ratios is not None
        else None
    )
    st.metric(
        "ROCE",
        fmt_percent(value),
    )

with k2:
    value = (
        latest_ratios["asset_turnover"]
        if latest_ratios is not None
        else None
    )
    st.metric(
        "Asset Turnover",
        fmt_number(value),
    )

with k3:
    value = (
        latest_ratios["cfo_margin_pct"]
        if latest_ratios is not None
        else None
    )
    st.metric(
        "CFO Margin",
        fmt_percent(value),
    )

with k4:
    value = (
        latest_ratios["cfo_pat_ratio"]
        if latest_ratios is not None
        else None
    )
    st.metric(
        "CFO / PAT",
        fmt_number(value),
    )


# ============================================================
# CASH FLOW SNAPSHOT
# ============================================================

st.subheader("Latest Cash Flow Snapshot")

c1, c2, c3, c4 = st.columns(4)

with c1:
    value = (
        latest_cf["operating_activity"]
        if latest_cf is not None
        else None
    )
    st.metric(
        "Operating Cash Flow",
        fmt_crore(value),
    )

with c2:
    value = (
        latest_cf["investing_activity"]
        if latest_cf is not None
        else None
    )
    st.metric(
        "Investing Cash Flow",
        fmt_crore(value),
    )

with c3:
    value = (
        latest_cf["financing_activity"]
        if latest_cf is not None
        else None
    )
    st.metric(
        "Financing Cash Flow",
        fmt_crore(value),
    )

with c4:
    value = (
        latest_cf["net_cash_flow"]
        if latest_cf is not None
        else None
    )
    st.metric(
        "Net Cash Flow",
        fmt_crore(value),
    )


# ============================================================
# BALANCE SHEET CAPITAL POSITION
# ============================================================

st.subheader("Balance-Sheet Capital Position")

b1, b2, b3, b4 = st.columns(4)

with b1:
    value = (
        latest_bs["borrowings"]
        if latest_bs is not None
        else None
    )
    st.metric(
        "Borrowings",
        fmt_crore(value),
    )

with b2:
    value = (
        latest_bs["reserves"]
        if latest_bs is not None
        else None
    )
    st.metric(
        "Reserves",
        fmt_crore(value),
    )

with b3:
    value = (
        latest_bs["investments"]
        if latest_bs is not None
        else None
    )
    st.metric(
        "Investments",
        fmt_crore(value),
    )

with b4:
    value = (
        latest_pl["dividend_payout"]
        if latest_pl is not None
        else None
    )
    st.metric(
        "Dividend Payout",
        fmt_percent(value),
    )


# ============================================================
# CASH FLOW HISTORY
# ============================================================

st.subheader("Cash Flow Allocation Trend")

if not cashflow.empty:

    cf_trend = (
        cashflow[
            [
                "year",
                "operating_activity",
                "investing_activity",
                "financing_activity",
                "net_cash_flow",
            ]
        ]
        .sort_values("year")
        .melt(
            id_vars="year",
            value_vars=[
                "operating_activity",
                "investing_activity",
                "financing_activity",
                "net_cash_flow",
            ],
            var_name="Cash Flow Type",
            value_name="₹ Crore",
        )
    )

    cf_trend["Cash Flow Type"] = (
        cf_trend["Cash Flow Type"]
        .replace(
            {
                "operating_activity":
                    "Operating",
                "investing_activity":
                    "Investing",
                "financing_activity":
                    "Financing",
                "net_cash_flow":
                    "Net Cash Flow",
            }
        )
    )

    cf_chart = px.line(
        cf_trend,
        x="year",
        y="₹ Crore",
        color="Cash Flow Type",
        markers=True,
        title=(
            "Operating, Investing and "
            "Financing Cash Flows"
        ),
    )

    st.plotly_chart(
        cf_chart,
        use_container_width=True,
    )

else:
    st.info(
        "Cash-flow history is unavailable."
    )


# ============================================================
# CAPITAL STRUCTURE TREND
# ============================================================

st.subheader("Capital Structure Trend")

if not balance_sheet.empty:

    capital_structure = (
        balance_sheet[
            [
                "year",
                "equity_capital",
                "reserves",
                "borrowings",
                "investments",
            ]
        ]
        .sort_values("year")
        .melt(
            id_vars="year",
            value_vars=[
                "equity_capital",
                "reserves",
                "borrowings",
                "investments",
            ],
            var_name="Metric",
            value_name="₹ Crore",
        )
    )

    capital_structure["Metric"] = (
        capital_structure["Metric"]
        .replace(
            {
                "equity_capital":
                    "Equity Capital",
                "reserves":
                    "Reserves",
                "borrowings":
                    "Borrowings",
                "investments":
                    "Investments",
            }
        )
    )

    capital_chart = px.line(
        capital_structure,
        x="year",
        y="₹ Crore",
        color="Metric",
        markers=True,
        title="Capital Structure History",
    )

    st.plotly_chart(
        capital_chart,
        use_container_width=True,
    )


# ============================================================
# CAPITAL EFFICIENCY HISTORY
# ============================================================

st.subheader("Capital Efficiency Trend")

if not ratios.empty:

    efficiency = (
        ratios[
            [
                "year",
                "roce_pct",
                "cfo_margin_pct",
                "asset_turnover",
                "cfo_pat_ratio",
            ]
        ]
        .sort_values("year")
    )

    e1, e2 = st.columns(2)

    with e1:
        percentage_data = (
            efficiency[
                [
                    "year",
                    "roce_pct",
                    "cfo_margin_pct",
                ]
            ]
            .melt(
                id_vars="year",
                value_vars=[
                    "roce_pct",
                    "cfo_margin_pct",
                ],
                var_name="Metric",
                value_name="Percent",
            )
        )

        percentage_data["Metric"] = (
            percentage_data["Metric"]
            .replace(
                {
                    "roce_pct": "ROCE",
                    "cfo_margin_pct":
                        "CFO Margin",
                }
            )
        )

        efficiency_chart = px.line(
            percentage_data,
            x="year",
            y="Percent",
            color="Metric",
            markers=True,
            title="ROCE & CFO Margin",
        )

        st.plotly_chart(
            efficiency_chart,
            use_container_width=True,
        )

    with e2:
        ratio_data = (
            efficiency[
                [
                    "year",
                    "asset_turnover",
                    "cfo_pat_ratio",
                ]
            ]
            .melt(
                id_vars="year",
                value_vars=[
                    "asset_turnover",
                    "cfo_pat_ratio",
                ],
                var_name="Metric",
                value_name="Ratio",
            )
        )

        ratio_data["Metric"] = (
            ratio_data["Metric"]
            .replace(
                {
                    "asset_turnover":
                        "Asset Turnover",
                    "cfo_pat_ratio":
                        "CFO / PAT",
                }
            )
        )

        ratio_chart = px.line(
            ratio_data,
            x="year",
            y="Ratio",
            color="Metric",
            markers=True,
            title=(
                "Asset Turnover & CFO/PAT"
            ),
        )

        st.plotly_chart(
            ratio_chart,
            use_container_width=True,
        )


# ============================================================
# SOURCE DATA
# ============================================================

with st.expander(
    "View capital allocation source data"
):

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Cash Flow",
            "Balance Sheet",
            "Ratios",
            "Profit & Loss",
        ]
    )

    with tab1:
        st.dataframe(
            cashflow,
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        st.dataframe(
            balance_sheet,
            use_container_width=True,
            hide_index=True,
        )

    with tab3:
        st.dataframe(
            ratios,
            use_container_width=True,
            hide_index=True,
        )

    with tab4:
        st.dataframe(
            profit_loss,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# DATA LIMITATION
# ============================================================

st.warning(
    "Explicit Capex and Free Cash Flow analytics are not "
    "displayed because the 2024-03 source dataset contains "
    "no populated values for FCF, FCF margin or Capex/Sales. "
    "The dashboard does not derive or fabricate those values "
    "from incomplete source fields."
)