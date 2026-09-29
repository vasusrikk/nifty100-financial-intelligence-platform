"""Sprint 5 - Day 31 & Day 32 Cash Flow Intelligence.

Day 31:
- CFO Quality Score
- Cash-flow distress pattern detection
- CapEx source assessment

Day 32:
- Capital Allocation Matrix
- Combined cashflow_intelligence.xlsx workbook

Important:
The source database does not contain an explicit CapEx field.
Investing cash flow is therefore NOT treated as CapEx.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"

CFO_QUALITY_OUTPUT = (
    OUTPUT_DIR
    / "cfo_quality_score.csv"
)

DISTRESS_OUTPUT = (
    OUTPUT_DIR
    / "cashflow_distress_flags.csv"
)

CAPITAL_MATRIX_OUTPUT = (
    OUTPUT_DIR
    / "capital_allocation_matrix.csv"
)

CASHFLOW_INTELLIGENCE_OUTPUT = (
    OUTPUT_DIR
    / "cashflow_intelligence.xlsx"
)


# ============================================================
# CONSTANTS
# ============================================================

LOOKBACK_YEARS = 5

CAPEX_SOURCE_UNAVAILABLE = (
    "CAPEX_SOURCE_UNAVAILABLE"
)


# ============================================================
# LOAD SOURCE DATA
# ============================================================

def load_cashflow_data():
    """
    Load cash-flow data together with matching sales
    and net-profit values from the SQLite database.
    """

    query = """
        SELECT
            cf.company_id,
            cf.year,
            cf.operating_activity,
            cf.investing_activity,
            cf.financing_activity,
            cf.net_cash_flow,
            p.sales,
            p.net_profit
        FROM cashflow cf
        LEFT JOIN profitandloss p
            ON cf.company_id = p.company_id
            AND cf.year = p.year
        ORDER BY
            cf.company_id,
            cf.year
    """

    with sqlite3.connect(
        DB_PATH
    ) as connection:

        frame = pd.read_sql_query(
            query,
            connection,
        )

    numeric_columns = [
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow",
        "sales",
        "net_profit",
    ]

    for column in numeric_columns:

        frame[column] = pd.to_numeric(
            frame[column],
            errors="coerce",
        )

    frame["fiscal_year"] = pd.to_numeric(
        frame["year"]
        .astype(str)
        .str[:4],
        errors="coerce",
    )

    return frame


# ============================================================
# DAY 31 - CFO QUALITY COMPONENTS
# ============================================================

def positive_cfo_score(history):
    """
    Score the consistency of positive operating cash flow.

    Maximum score: 30.
    """

    available = history[
        "operating_activity"
    ].dropna()

    if available.empty:
        return 0.0

    positive_ratio = (
        available.gt(0).sum()
        / len(available)
    )

    return positive_ratio * 30.0


def cfo_pat_score(history):
    """
    Measure operating cash-flow conversion of positive PAT.

    Median CFO/PAT >= 1 receives full credit.

    Maximum score: 30.
    """

    valid = history[
        history["net_profit"].notna()
        & history["operating_activity"].notna()
        & history["net_profit"].gt(0)
    ].copy()

    if valid.empty:
        return 0.0

    valid["cfo_pat_ratio"] = (
        valid["operating_activity"]
        / valid["net_profit"]
    )

    median_ratio = valid[
        "cfo_pat_ratio"
    ].median()

    if pd.isna(
        median_ratio
    ):
        return 0.0

    bounded_ratio = max(
        0.0,
        min(
            float(median_ratio),
            1.0,
        ),
    )

    return bounded_ratio * 30.0


def cfo_margin_score(history):
    """
    Score median CFO Margin.

    Full credit is reached at a median CFO Margin
    of 15 percent.

    Maximum score: 20.
    """

    valid = history[
        history["sales"].notna()
        & history["operating_activity"].notna()
        & history["sales"].ne(0)
    ].copy()

    if valid.empty:
        return 0.0

    valid["cfo_margin_pct"] = (
        valid["operating_activity"]
        / valid["sales"]
    ) * 100

    median_margin = valid[
        "cfo_margin_pct"
    ].median()

    if pd.isna(
        median_margin
    ):
        return 0.0

    bounded_margin = max(
        0.0,
        min(
            float(median_margin),
            15.0,
        ),
    )

    return (
        bounded_margin
        / 15.0
    ) * 20.0


def cfo_stability_score(history):
    """
    Reward stable positive CFO history.

    Maximum score: 20.
    """

    cfo = history[
        "operating_activity"
    ].dropna()

    if cfo.empty:
        return 0.0

    positive_ratio = (
        cfo.gt(0).sum()
        / len(cfo)
    )

    if len(cfo) < 2:

        trend_component = 0.5

    else:

        first_value = float(
            cfo.iloc[0]
        )

        last_value = float(
            cfo.iloc[-1]
        )

        if last_value >= first_value:
            trend_component = 1.0
        else:
            trend_component = 0.0

    stability = (
        positive_ratio * 0.75
        + trend_component * 0.25
    )

    return stability * 20.0


def quality_class(score):
    """
    Convert CFO Quality Score into a quality band.
    """

    if score >= 80:
        return "STRONG"

    if score >= 60:
        return "GOOD"

    if score >= 40:
        return "MODERATE"

    return "WEAK"


# ============================================================
# DAY 31 - BUILD CFO QUALITY SCORE
# ============================================================

def build_cfo_quality_score():
    """
    Build one CFO Quality Score per company using the
    latest five available observations.
    """

    frame = load_cashflow_data()

    results = []

    for (
        company_id,
        company,
    ) in frame.groupby(
        "company_id"
    ):

        company = company.sort_values(
            [
                "fiscal_year",
                "year",
            ]
        )

        history = company.tail(
            LOOKBACK_YEARS
        ).copy()

        positive_score = (
            positive_cfo_score(
                history
            )
        )

        conversion_score = (
            cfo_pat_score(
                history
            )
        )

        margin_score = (
            cfo_margin_score(
                history
            )
        )

        stability_score = (
            cfo_stability_score(
                history
            )
        )

        total_score = (
            positive_score
            + conversion_score
            + margin_score
            + stability_score
        )

        total_score = round(
            total_score,
            2,
        )

        cfo_values = history[
            "operating_activity"
        ].dropna()

        positive_years = int(
            cfo_values.gt(0).sum()
        )

        negative_years = int(
            cfo_values.lt(0).sum()
        )

        results.append(
            {
                "company_id":
                    company_id,

                "observations_used":
                    len(history),

                "positive_cfo_years":
                    positive_years,

                "negative_cfo_years":
                    negative_years,

                "positive_cfo_score":
                    round(
                        positive_score,
                        2,
                    ),

                "cfo_pat_score":
                    round(
                        conversion_score,
                        2,
                    ),

                "cfo_margin_score":
                    round(
                        margin_score,
                        2,
                    ),

                "cfo_stability_score":
                    round(
                        stability_score,
                        2,
                    ),

                "cfo_quality_score":
                    total_score,

                "cfo_quality_class":
                    quality_class(
                        total_score
                    ),
            }
        )

    return pd.DataFrame(
        results
    )


def save_cfo_quality_score(
    frame,
):
    """Save CFO Quality Score CSV."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    frame.to_csv(
        CFO_QUALITY_OUTPUT,
        index=False,
    )


def print_quality_summary(
    frame,
):
    """Print CFO Quality Score QA."""

    print(
        "DAY 31 CFO QUALITY SCORE COMPLETE"
    )

    print(
        "COMPANIES:",
        frame[
            "company_id"
        ].nunique(),
    )

    print(
        "ROWS:",
        len(frame),
    )

    print(
        "\nQUALITY CLASS DISTRIBUTION:"
    )

    print(
        frame[
            "cfo_quality_class"
        ].value_counts()
    )

    print(
        "\nSCORE RANGE:"
    )

    print(
        "MIN:",
        round(
            frame[
                "cfo_quality_score"
            ].min(),
            2,
        ),
    )

    print(
        "MAX:",
        round(
            frame[
                "cfo_quality_score"
            ].max(),
            2,
        ),
    )

    print(
        "\nOUTPUT:",
        CFO_QUALITY_OUTPUT,
    )


# ============================================================
# DAY 31 - DISTRESS PATTERN ENGINE
# ============================================================

def detect_distress_patterns():
    """
    Detect five company-level cash-flow distress patterns.

    Patterns:
    1. Repeated negative CFO
    2. Persistent CFO below PAT
    3. Declining CFO trend
    4. Negative latest CFO
    5. Financing dependence
    """

    frame = load_cashflow_data()

    results = []

    for (
        company_id,
        company,
    ) in frame.groupby(
        "company_id"
    ):

        company = company.sort_values(
            [
                "fiscal_year",
                "year",
            ]
        )

        history = company.tail(
            LOOKBACK_YEARS
        ).copy()

        cfo = history[
            "operating_activity"
        ]

        financing = history[
            "financing_activity"
        ]

        # ----------------------------------------------------
        # FLAG 1 - REPEATED NEGATIVE CFO
        # ----------------------------------------------------

        negative_cfo_count = int(
            cfo.dropna()
            .lt(0)
            .sum()
        )

        repeated_negative_cfo = (
            negative_cfo_count >= 2
        )

        # ----------------------------------------------------
        # FLAG 2 - CFO BELOW PAT
        # ----------------------------------------------------

        comparable = history[
            history[
                "operating_activity"
            ].notna()
            &
            history[
                "net_profit"
            ].notna()
            &
            history[
                "net_profit"
            ].gt(0)
        ].copy()

        if comparable.empty:

            cfo_below_pat_count = 0

        else:

            cfo_below_pat_count = int(
                (
                    comparable[
                        "operating_activity"
                    ]
                    <
                    comparable[
                        "net_profit"
                    ]
                ).sum()
            )

        persistent_cfo_below_pat = (
            cfo_below_pat_count >= 3
        )

        # ----------------------------------------------------
        # FLAG 3 - DECLINING CFO TREND
        # ----------------------------------------------------

        valid_cfo = cfo.dropna()

        if len(valid_cfo) >= 3:

            recent_changes = (
                valid_cfo
                .diff()
                .dropna()
            )

            declining_steps = int(
                recent_changes
                .lt(0)
                .sum()
            )

            declining_cfo_trend = (
                declining_steps
                >= max(
                    2,
                    len(recent_changes) - 1,
                )
            )

        else:

            declining_steps = 0
            declining_cfo_trend = False

        # ----------------------------------------------------
        # FLAG 4 - NEGATIVE LATEST CFO
        # ----------------------------------------------------

        if valid_cfo.empty:

            latest_cfo = None
            negative_latest_cfo = False

        else:

            latest_cfo = float(
                valid_cfo.iloc[-1]
            )

            negative_latest_cfo = (
                latest_cfo < 0
            )

        # ----------------------------------------------------
        # FLAG 5 - FINANCING DEPENDENCE
        # ----------------------------------------------------

        valid_financing = (
            financing.dropna()
        )

        positive_financing_years = int(
            valid_financing
            .gt(0)
            .sum()
        )

        financing_dependence = (
            positive_financing_years >= 3
        )

        # ----------------------------------------------------
        # DISTRESS SCORE
        # ----------------------------------------------------

        distress_score = sum(
            [
                (
                    2
                    if repeated_negative_cfo
                    else 0
                ),
                (
                    2
                    if persistent_cfo_below_pat
                    else 0
                ),
                (
                    1
                    if declining_cfo_trend
                    else 0
                ),
                (
                    2
                    if negative_latest_cfo
                    else 0
                ),
                (
                    1
                    if financing_dependence
                    else 0
                ),
            ]
        )

        if distress_score >= 5:

            distress_level = "HIGH"

        elif distress_score >= 3:

            distress_level = "MODERATE"

        elif distress_score >= 1:

            distress_level = "LOW"

        else:

            distress_level = "NONE"

        results.append(
            {
                "company_id":
                    company_id,

                "observations_used":
                    len(history),

                "negative_cfo_count":
                    negative_cfo_count,

                "repeated_negative_cfo":
                    repeated_negative_cfo,

                "cfo_below_pat_count":
                    cfo_below_pat_count,

                "persistent_cfo_below_pat":
                    persistent_cfo_below_pat,

                "declining_cfo_steps":
                    declining_steps,

                "declining_cfo_trend":
                    declining_cfo_trend,

                "latest_cfo":
                    latest_cfo,

                "negative_latest_cfo":
                    negative_latest_cfo,

                "positive_financing_years":
                    positive_financing_years,

                "financing_dependence":
                    financing_dependence,

                "distress_score":
                    distress_score,

                "distress_level":
                    distress_level,
            }
        )

    return pd.DataFrame(
        results
    )


def save_distress_flags(
    frame,
):
    """Save distress flags CSV."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    frame.to_csv(
        DISTRESS_OUTPUT,
        index=False,
    )


def print_distress_summary(
    frame,
):
    """Print distress-pattern QA."""

    print(
        "\nDAY 31 DISTRESS PATTERN ANALYSIS COMPLETE"
    )

    print(
        "COMPANIES:",
        frame[
            "company_id"
        ].nunique(),
    )

    print(
        "ROWS:",
        len(frame),
    )

    print(
        "\nDISTRESS LEVEL DISTRIBUTION:"
    )

    print(
        frame[
            "distress_level"
        ].value_counts()
    )

    print(
        "\nFLAGS:"
    )

    flag_columns = [
        "repeated_negative_cfo",
        "persistent_cfo_below_pat",
        "declining_cfo_trend",
        "negative_latest_cfo",
        "financing_dependence",
    ]

    for column in flag_columns:

        print(
            column,
            ":",
            int(
                frame[column]
                .fillna(False)
                .sum()
            ),
        )

    print(
        "\nOUTPUT:",
        DISTRESS_OUTPUT,
    )


# ============================================================
# DAY 32 - CAPITAL ALLOCATION CLASSIFICATION
# ============================================================

def classify_capital_allocation(
    cfo,
    investing,
    financing,
    net_cash,
):
    """
    Classify observed capital-allocation behaviour.

    Investing cash flow is NOT interpreted as CapEx.
    """

    if (
        pd.isna(cfo)
        and pd.isna(investing)
        and pd.isna(financing)
    ):

        return (
            "INSUFFICIENT_DATA",
            "Insufficient cash-flow evidence.",
        )

    if (
        pd.notna(cfo)
        and pd.notna(investing)
        and pd.notna(financing)
        and cfo > 0
        and investing < 0
        and financing <= 0
    ):

        return (
            "INTERNALLY_FUNDED_INVESTMENT",
            "Positive operating cash flow supports "
            "investing outflows without positive "
            "external financing.",
        )

    if (
        pd.notna(cfo)
        and pd.notna(investing)
        and pd.notna(financing)
        and investing < 0
        and financing > 0
    ):

        return (
            "EXTERNALLY_FUNDED_INVESTMENT",
            "Investing outflows occur alongside "
            "positive financing cash flow.",
        )

    if (
        pd.notna(cfo)
        and pd.notna(financing)
        and cfo <= 0
        and financing > 0
    ):

        return (
            "FINANCING_DEPENDENT",
            "Weak or negative operating cash flow "
            "coincides with positive financing cash flow.",
        )

    if (
        pd.notna(cfo)
        and pd.notna(net_cash)
        and cfo > 0
        and net_cash > 0
    ):

        return (
            "CASH_ACCUMULATION",
            "Positive operating cash flow contributes "
            "to an increase in net cash.",
        )

    if (
        pd.notna(investing)
        and investing > 0
    ):

        return (
            "INVESTING_INFLOW",
            "Positive investing cash flow indicates "
            "net investing inflows; source-level review "
            "is required to determine the transactions.",
        )

    return (
        "MIXED",
        "Cash-flow pattern does not fit one dominant "
        "capital-allocation category.",
    )


# ============================================================
# DAY 32 - BUILD CAPITAL ALLOCATION MATRIX
# ============================================================

def build_capital_allocation_matrix():
    """
    Build one capital-allocation record per company using
    latest cash-flow evidence and five-observation history.
    """

    frame = load_cashflow_data()

    results = []

    for (
        company_id,
        company,
    ) in frame.groupby(
        "company_id"
    ):

        company = company.sort_values(
            [
                "fiscal_year",
                "year",
            ]
        )

        history = company.tail(
            LOOKBACK_YEARS
        ).copy()

        latest = history.iloc[-1]

        cfo = latest[
            "operating_activity"
        ]

        investing = latest[
            "investing_activity"
        ]

        financing = latest[
            "financing_activity"
        ]

        net_cash = latest[
            "net_cash_flow"
        ]

        (
            allocation_class,
            allocation_explanation,
        ) = classify_capital_allocation(
            cfo,
            investing,
            financing,
            net_cash,
        )

        positive_cfo_years = int(
            history[
                "operating_activity"
            ]
            .dropna()
            .gt(0)
            .sum()
        )

        investing_outflow_years = int(
            history[
                "investing_activity"
            ]
            .dropna()
            .lt(0)
            .sum()
        )

        positive_financing_years = int(
            history[
                "financing_activity"
            ]
            .dropna()
            .gt(0)
            .sum()
        )

        positive_net_cash_years = int(
            history[
                "net_cash_flow"
            ]
            .dropna()
            .gt(0)
            .sum()
        )

        results.append(
            {
                "company_id":
                    company_id,

                "latest_year":
                    latest["year"],

                "observations_used":
                    len(history),

                "latest_cfo":
                    cfo,

                "latest_investing_cf":
                    investing,

                "latest_financing_cf":
                    financing,

                "latest_net_cash_flow":
                    net_cash,

                "positive_cfo_years":
                    positive_cfo_years,

                "investing_outflow_years":
                    investing_outflow_years,

                "positive_financing_years":
                    positive_financing_years,

                "positive_net_cash_years":
                    positive_net_cash_years,

                "allocation_class":
                    allocation_class,

                "allocation_explanation":
                    allocation_explanation,

                "capex_intensity_pct":
                    None,

                "capex_status":
                    CAPEX_SOURCE_UNAVAILABLE,
            }
        )

    return pd.DataFrame(
        results
    )


def save_capital_allocation_matrix(
    frame,
):
    """Save Capital Allocation Matrix CSV."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    frame.to_csv(
        CAPITAL_MATRIX_OUTPUT,
        index=False,
    )


def print_capital_matrix_summary(
    frame,
):
    """Print Capital Allocation Matrix QA."""

    print(
        "\nDAY 32 CAPITAL ALLOCATION MATRIX COMPLETE"
    )

    print(
        "COMPANIES:",
        frame[
            "company_id"
        ].nunique(),
    )

    print(
        "ROWS:",
        len(frame),
    )

    print(
        "\nALLOCATION CLASS DISTRIBUTION:"
    )

    print(
        frame[
            "allocation_class"
        ].value_counts()
    )

    print(
        "\nCAPEX INTENSITY:"
    )

    print(
        "AVAILABLE:",
        frame[
            "capex_intensity_pct"
        ].notna()
        .sum(),
    )

    print(
        "UNAVAILABLE:",
        frame[
            "capex_intensity_pct"
        ].isna()
        .sum(),
    )

    print(
        "STATUS:",
        CAPEX_SOURCE_UNAVAILABLE,
    )

    print(
        "\nOUTPUT:",
        CAPITAL_MATRIX_OUTPUT,
    )


# ============================================================
# DAY 32 - COMBINED EXCEL WORKBOOK
# ============================================================

def build_cashflow_intelligence_workbook(
    quality,
    distress,
    capital_matrix,
):
    """
    Create the complete Sprint 5 cash-flow intelligence
    Excel workbook.
    """

    summary = quality.merge(
        distress,
        on="company_id",
        how="outer",
        suffixes=(
            "_quality",
            "_distress",
        ),
    )

    summary = summary.merge(
        capital_matrix,
        on="company_id",
        how="outer",
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        CASHFLOW_INTELLIGENCE_OUTPUT,
        engine="openpyxl",
    ) as writer:

        summary.to_excel(
            writer,
            sheet_name="Company Summary",
            index=False,
        )

        quality.to_excel(
            writer,
            sheet_name="CFO Quality",
            index=False,
        )

        distress.to_excel(
            writer,
            sheet_name="Distress Flags",
            index=False,
        )

        capital_matrix.to_excel(
            writer,
            sheet_name="Capital Allocation",
            index=False,
        )

    return summary


def print_workbook_summary(
    summary,
):
    """Print final workbook QA."""

    print(
        "\nDAY 32 CASHFLOW INTELLIGENCE WORKBOOK COMPLETE"
    )

    print(
        "SUMMARY ROWS:",
        len(summary),
    )

    print(
        "COMPANIES:",
        summary[
            "company_id"
        ].nunique(),
    )

    print(
        "SHEETS: 4"
    )

    print(
        "1. Company Summary"
    )

    print(
        "2. CFO Quality"
    )

    print(
        "3. Distress Flags"
    )

    print(
        "4. Capital Allocation"
    )

    print(
        "\nOUTPUT:",
        CASHFLOW_INTELLIGENCE_OUTPUT,
    )


# ============================================================
# MAIN
# ============================================================

def main():
    """
    Execute the complete Sprint 5 Day 31-32
    Cash Flow Intelligence pipeline.
    """

    # --------------------------------------------------------
    # DAY 31 - CFO QUALITY
    # --------------------------------------------------------

    quality = (
        build_cfo_quality_score()
    )

    save_cfo_quality_score(
        quality
    )

    print_quality_summary(
        quality
    )

    # --------------------------------------------------------
    # DAY 31 - DISTRESS PATTERNS
    # --------------------------------------------------------

    distress = (
        detect_distress_patterns()
    )

    save_distress_flags(
        distress
    )

    print_distress_summary(
        distress
    )

    # --------------------------------------------------------
    # DAY 32 - CAPITAL ALLOCATION MATRIX
    # --------------------------------------------------------

    capital_matrix = (
        build_capital_allocation_matrix()
    )

    save_capital_allocation_matrix(
        capital_matrix
    )

    print_capital_matrix_summary(
        capital_matrix
    )

    # --------------------------------------------------------
    # DAY 32 - FINAL EXCEL WORKBOOK
    # --------------------------------------------------------

    summary = (
        build_cashflow_intelligence_workbook(
            quality,
            distress,
            capital_matrix,
        )
    )

    print_workbook_summary(
        summary
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()