"""Sprint 4 - Day 24: Interactive Company Screener."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.screener.engine import run_screener
from src.screener.scoring import rank_companies


# ============================================================
# CONFIGURATION
# ============================================================

METRIC_LABELS = {
    "roe_pct": "ROE (%)",
    "roce_pct": "ROCE (%)",
    "npm_pct": "Net Profit Margin (%)",
    "opm_pct": "Operating Profit Margin (%)",
    "de_ratio": "Debt / Equity",
    "icr": "Interest Coverage Ratio",
    "asset_turnover": "Asset Turnover",
    "revenue_cagr_5yr": "Revenue CAGR 5yr (%)",
    "pat_cagr_5yr": "PAT CAGR 5yr (%)",
    "eps_cagr_5yr": "EPS CAGR 5yr (%)",
    "cfo_margin_pct": "CFO Margin (%)",
    "market_cap_crore": "Market Cap (₹ Cr)",
    "pe_ratio": "P/E",
    "pb_ratio": "P/B",
    "dividend_yield_pct": "Dividend Yield (%)",
}

OPERATORS = [
    ">=",
    ">",
    "<=",
    "<",
    "==",
]


# ============================================================
# HEADER
# ============================================================

st.title("Company Screener")

st.caption(
    "Filter the NIFTY 100 universe using the existing "
    "Sprint 3 fundamental screening and scoring engines."
)


# ============================================================
# FILTER BUILDER
# ============================================================

st.subheader("Build Screener")

filter_count = st.number_input(
    "Number of filters",
    min_value=1,
    max_value=8,
    value=3,
    step=1,
)

filters = []

metric_names = list(
    METRIC_LABELS.keys()
)

default_metrics = [
    "roe_pct",
    "de_ratio",
    "revenue_cagr_5yr",
]

for index in range(
    int(filter_count)
):
    st.markdown(
        f"**Filter {index + 1}**"
    )

    col1, col2, col3 = st.columns(
        [2, 1, 1]
    )

    default_metric = (
        default_metrics[index]
        if index < len(default_metrics)
        else metric_names[index % len(metric_names)]
    )

    with col1:
        metric = st.selectbox(
            "Metric",
            options=metric_names,
            index=metric_names.index(
                default_metric
            ),
            format_func=lambda x: (
                METRIC_LABELS[x]
            ),
            key=f"metric_{index}",
        )

    with col2:
        operator = st.selectbox(
            "Operator",
            options=OPERATORS,
            key=f"operator_{index}",
        )

    with col3:
        default_value = 0.0

        if metric == "roe_pct":
            default_value = 15.0

        elif metric == "de_ratio":
            default_value = 1.0

        elif metric == "revenue_cagr_5yr":
            default_value = 10.0

        value = st.number_input(
            "Value",
            value=default_value,
            step=0.5,
            key=f"value_{index}",
        )

    filters.append(
        {
            "metric": metric,
            "operator": operator,
            "value": float(value),
        }
    )


# ============================================================
# RUN SCREENER
# ============================================================

run_button = st.button(
    "Run Screener",
    type="primary",
    use_container_width=True,
)

if run_button:

    try:
        results = run_screener(
            filters
        )

        st.session_state[
            "screener_results"
        ] = results

        st.session_state[
            "screener_filters"
        ] = filters

    except Exception as exc:
        st.error(
            f"Screener failed: {exc}"
        )


# ============================================================
# RESULTS
# ============================================================

if "screener_results" in st.session_state:

    results = st.session_state[
        "screener_results"
    ]

    st.divider()

    st.subheader("Results")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Matching Companies",
            len(results),
        )

    with c2:
        st.metric(
            "Universe",
            92,
        )

    if results:

        # ----------------------------------------------------
        # SCORE MATCHING COMPANIES
        # ----------------------------------------------------

        ranked = rank_companies(
            results
        )

        ranked_lookup = {
            row["company_id"]: row
            for row in ranked
        }

        display_rows = []

        for row in results:

            company_id = row.get(
                "company_id"
            )

            scored = ranked_lookup.get(
                company_id,
                {},
            )

            display_rows.append(
                {
                    "Ticker":
                        company_id,

                    "Company":
                        row.get(
                            "company_name"
                        ),

                    "Sector":
                        row.get(
                            "broad_sector"
                        ),

                    "ROE (%)":
                        row.get(
                            "roe_pct"
                        ),

                    "ROCE (%)":
                        row.get(
                            "roce_pct"
                        ),

                    "D/E":
                        row.get(
                            "de_ratio"
                        ),

                    "Revenue CAGR 5yr (%)":
                        row.get(
                            "revenue_cagr_5yr"
                        ),

                    "P/E":
                        row.get(
                            "pe_ratio"
                        ),

                    "Market Cap (₹ Cr)":
                        row.get(
                            "market_cap_crore"
                        ),

                    "Composite Score":
                        scored.get(
                            "composite_score"
                        ),

                    "Score Coverage (%)":
                        scored.get(
                            "score_coverage_pct"
                        ),
                }
            )

        result_df = pd.DataFrame(
            display_rows
        )

        if (
            "Composite Score"
            in result_df.columns
        ):
            result_df = (
                result_df.sort_values(
                    [
                        "Composite Score",
                        "Score Coverage (%)",
                    ],
                    ascending=[
                        False,
                        False,
                    ],
                    na_position="last",
                )
            )

        result_df.insert(
            0,
            "Rank",
            range(
                1,
                len(result_df) + 1,
            ),
        )

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # CSV EXPORT
        # ----------------------------------------------------

        csv_data = (
            result_df.to_csv(
                index=False
            )
            .encode("utf-8")
        )

        st.download_button(
            label="Download Results as CSV",
            data=csv_data,
            file_name=(
                "nifty100_screener_results.csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )


        # ----------------------------------------------------
        # ACTIVE FILTERS
        # ----------------------------------------------------

        with st.expander(
            "View active filters"
        ):

            active_filters = (
                st.session_state[
                    "screener_filters"
                ]
            )

            for rule in active_filters:

                metric_label = (
                    METRIC_LABELS[
                        rule["metric"]
                    ]
                )

                st.write(
                    f"{metric_label} "
                    f"{rule['operator']} "
                    f"{rule['value']}"
                )

    else:
        st.warning(
            "No companies match the selected filters."
        )


# ============================================================
# ENGINE NOTES
# ============================================================

st.caption(
    "The screener uses the existing project screening engine. "
    "Financial-sector companies retain the engine's D/E "
    "carve-out, and debt-free companies retain its special "
    "minimum-ICR handling. Missing source metrics are not "
    "fabricated."
)