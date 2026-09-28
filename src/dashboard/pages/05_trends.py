"""Sprint 4 - Day 25: Historical Trends Dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard.utils.db import (
    get_companies,
    get_pl,
    get_ratios,
    get_stock_prices,
)


# ============================================================
# HELPERS
# ============================================================

def safe_cagr(start_value, end_value, periods):
    """
    Calculate CAGR only when mathematically valid.
    """

    if (
        start_value is None
        or end_value is None
        or periods <= 0
        or pd.isna(start_value)
        or pd.isna(end_value)
        or start_value <= 0
        or end_value <= 0
    ):
        return None

    return (
        (
            end_value / start_value
        ) ** (1 / periods)
        - 1
    ) * 100


def fmt_percent(value):
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


def fmt_number(value):
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:,.2f}"


# ============================================================
# HEADER
# ============================================================

st.title("Historical Trends")

st.caption(
    "Explore company price performance, financial growth "
    "and profitability trends using the project's historical data."
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

prices = get_stock_prices(
    selected_company
).copy()

pl = get_pl(
    selected_company
).copy()

ratios = get_ratios(
    selected_company
).copy()


# ============================================================
# STOCK PRICE SUMMARY
# ============================================================

st.subheader("Stock Price Performance")

if not prices.empty:

    prices["date"] = pd.to_datetime(
        prices["date"]
    )

    prices = prices.sort_values(
        "date"
    )

    price_column = (
        "adjusted_close"
        if (
            "adjusted_close"
            in prices.columns
            and prices["adjusted_close"]
            .notna()
            .any()
        )
        else "close_price"
    )

    valid_prices = prices.dropna(
        subset=[price_column]
    )

    if not valid_prices.empty:

        first_price = float(
            valid_prices.iloc[0][
                price_column
            ]
        )

        last_price = float(
            valid_prices.iloc[-1][
                price_column
            ]
        )

        first_date = (
            valid_prices.iloc[0]["date"]
        )

        last_date = (
            valid_prices.iloc[-1]["date"]
        )

        years = (
            last_date - first_date
        ).days / 365.25

        price_return = (
            (
                last_price / first_price
                - 1
            ) * 100
            if first_price > 0
            else None
        )

        price_cagr = safe_cagr(
            first_price,
            last_price,
            years,
        )

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.metric(
                "First Price",
                fmt_number(first_price),
            )

        with k2:
            st.metric(
                "Latest Price",
                fmt_number(last_price),
            )

        with k3:
            st.metric(
                "Total Return",
                fmt_percent(price_return),
            )

        with k4:
            st.metric(
                "Price CAGR",
                fmt_percent(price_cagr),
            )

        price_chart = px.line(
            valid_prices,
            x="date",
            y=price_column,
            markers=True,
            title=(
                f"{selected_company} "
                "Historical Stock Price"
            ),
            labels={
                "date": "Date",
                price_column: "Price",
            },
        )

        st.plotly_chart(
            price_chart,
            use_container_width=True,
        )

    else:
        st.info(
            "No usable stock-price values "
            "are available."
        )

else:
    st.info(
        "Stock-price history is unavailable "
        "for this company."
    )


# ============================================================
# REVENUE & PROFIT TREND
# ============================================================

st.subheader(
    "Revenue & Profit Trend"
)

if not pl.empty:

    pl = pl.sort_values(
        "year"
    )

    financial_trend = (
        pl[
            [
                "year",
                "sales",
                "operating_profit",
                "net_profit",
            ]
        ]
        .melt(
            id_vars="year",
            value_vars=[
                "sales",
                "operating_profit",
                "net_profit",
            ],
            var_name="Metric",
            value_name="₹ Crore",
        )
    )

    financial_trend["Metric"] = (
        financial_trend["Metric"]
        .replace(
            {
                "sales": "Revenue",
                "operating_profit":
                    "Operating Profit",
                "net_profit":
                    "Net Profit",
            }
        )
    )

    financial_chart = px.line(
        financial_trend,
        x="year",
        y="₹ Crore",
        color="Metric",
        markers=True,
        title=(
            "Revenue, Operating Profit "
            "and Net Profit"
        ),
    )

    st.plotly_chart(
        financial_chart,
        use_container_width=True,
    )

else:
    st.info(
        "Profit and loss history "
        "is unavailable."
    )


# ============================================================
# PROFITABILITY TREND
# ============================================================

st.subheader(
    "Profitability & Return Trend"
)

if not ratios.empty:

    ratios = ratios.sort_values(
        "year"
    )

    profitability = (
        ratios[
            [
                "year",
                "roe_pct",
                "roce_pct",
                "npm_pct",
                "opm_pct",
            ]
        ]
        .melt(
            id_vars="year",
            value_vars=[
                "roe_pct",
                "roce_pct",
                "npm_pct",
                "opm_pct",
            ],
            var_name="Metric",
            value_name="Percent",
        )
    )

    profitability["Metric"] = (
        profitability["Metric"]
        .replace(
            {
                "roe_pct": "ROE",
                "roce_pct": "ROCE",
                "npm_pct":
                    "Net Profit Margin",
                "opm_pct":
                    "Operating Profit Margin",
            }
        )
    )

    profitability_chart = px.line(
        profitability,
        x="year",
        y="Percent",
        color="Metric",
        markers=True,
        title=(
            "ROE, ROCE and Profitability Margins"
        ),
    )

    st.plotly_chart(
        profitability_chart,
        use_container_width=True,
    )

else:
    st.info(
        "Financial-ratio history "
        "is unavailable."
    )


# ============================================================
# GROWTH TREND
# ============================================================

st.subheader("Five-Year Growth Metrics")

if not ratios.empty:

    growth = (
        ratios[
            [
                "year",
                "revenue_cagr_5yr",
                "pat_cagr_5yr",
                "eps_cagr_5yr",
            ]
        ]
        .melt(
            id_vars="year",
            value_vars=[
                "revenue_cagr_5yr",
                "pat_cagr_5yr",
                "eps_cagr_5yr",
            ],
            var_name="Metric",
            value_name="CAGR (%)",
        )
    )

    growth["Metric"] = (
        growth["Metric"]
        .replace(
            {
                "revenue_cagr_5yr":
                    "Revenue CAGR 5yr",
                "pat_cagr_5yr":
                    "PAT CAGR 5yr",
                "eps_cagr_5yr":
                    "EPS CAGR 5yr",
            }
        )
    )

    growth_chart = px.line(
        growth,
        x="year",
        y="CAGR (%)",
        color="Metric",
        markers=True,
        title="Five-Year Growth History",
    )

    st.plotly_chart(
        growth_chart,
        use_container_width=True,
    )


# ============================================================
# HISTORICAL DATA
# ============================================================

with st.expander(
    "View historical source data"
):

    tab1, tab2, tab3 = st.tabs(
        [
            "Stock Prices",
            "Profit & Loss",
            "Financial Ratios",
        ]
    )

    with tab1:
        st.dataframe(
            prices,
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        st.dataframe(
            pl,
            use_container_width=True,
            hide_index=True,
        )

    with tab3:
        st.dataframe(
            ratios,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# SOURCE NOTE
# ============================================================

st.caption(
    "Historical charts use source values stored in the "
    "project database. Stock-price history contains monthly "
    "observations from 2020 through 2024. Missing financial "
    "values are not interpolated or fabricated."
)