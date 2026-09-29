"""Sprint 5 - Day 30: Automatic Pros and Cons Generator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "output"
    / "analysis_parsed.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "output"
    / "pros_cons.csv"
)


# ============================================================
# HELPERS
# ============================================================

def valid(value):
    """Return True when a metric contains a usable value."""

    return (
        value is not None
        and not pd.isna(value)
    )


def add_signal(
    signals,
    rule_id,
    metric,
    value,
    period,
    message,
):
    """Add one generated financial signal."""

    signals.append(
        {
            "rule_id": rule_id,
            "metric": metric,
            "period": period,
            "value_pct": value,
            "message": message,
        }
    )


def period_label(period_years):
    """Convert normalized period value into readable text."""

    if pd.isna(period_years):
        return "Unknown Period"

    period_years = int(period_years)

    if period_years == 0:
        return "TTM"

    if period_years == 1:
        return "1 Year"

    return f"{period_years} Years"


# ============================================================
# 12 PRO RULES
# ============================================================

def generate_pros(
    metric_type,
    value,
    period,
):
    """Generate positive signals using 12 explicit rules."""

    pros = []

    if not valid(value):
        return pros

    value = float(value)

    # --------------------------------------------------------
    # REVENUE CAGR - 3 PRO RULES
    # --------------------------------------------------------

    if metric_type == "revenue_cagr":

        if value >= 20:
            add_signal(
                pros,
                "PRO_01",
                "Revenue CAGR",
                value,
                period,
                f"Excellent revenue growth of {value:.2f}%.",
            )

        elif 10 <= value < 20:
            add_signal(
                pros,
                "PRO_02",
                "Revenue CAGR",
                value,
                period,
                f"Healthy revenue growth of {value:.2f}%.",
            )

        elif 5 <= value < 10:
            add_signal(
                pros,
                "PRO_03",
                "Revenue CAGR",
                value,
                period,
                f"Positive revenue growth of {value:.2f}%.",
            )

    # --------------------------------------------------------
    # PAT CAGR - 3 PRO RULES
    # --------------------------------------------------------

    elif metric_type == "pat_cagr":

        if value >= 20:
            add_signal(
                pros,
                "PRO_04",
                "PAT CAGR",
                value,
                period,
                f"Excellent profit growth of {value:.2f}%.",
            )

        elif 10 <= value < 20:
            add_signal(
                pros,
                "PRO_05",
                "PAT CAGR",
                value,
                period,
                f"Healthy profit growth of {value:.2f}%.",
            )

        elif 5 <= value < 10:
            add_signal(
                pros,
                "PRO_06",
                "PAT CAGR",
                value,
                period,
                f"Positive profit growth of {value:.2f}%.",
            )

    # --------------------------------------------------------
    # STOCK PRICE CAGR - 3 PRO RULES
    # --------------------------------------------------------

    elif metric_type == "stock_price_cagr":

        if value >= 20:
            add_signal(
                pros,
                "PRO_07",
                "Stock Price CAGR",
                value,
                period,
                f"Strong stock-price CAGR of {value:.2f}%.",
            )

        elif 10 <= value < 20:
            add_signal(
                pros,
                "PRO_08",
                "Stock Price CAGR",
                value,
                period,
                f"Healthy stock-price CAGR of {value:.2f}%.",
            )

        elif 5 <= value < 10:
            add_signal(
                pros,
                "PRO_09",
                "Stock Price CAGR",
                value,
                period,
                f"Positive stock-price CAGR of {value:.2f}%.",
            )

    # --------------------------------------------------------
    # ROE - 3 PRO RULES
    # --------------------------------------------------------

    elif metric_type == "roe":

        if value >= 25:
            add_signal(
                pros,
                "PRO_10",
                "ROE",
                value,
                period,
                f"Excellent return on equity of {value:.2f}%.",
            )

        elif 15 <= value < 25:
            add_signal(
                pros,
                "PRO_11",
                "ROE",
                value,
                period,
                f"Healthy return on equity of {value:.2f}%.",
            )

        elif 10 <= value < 15:
            add_signal(
                pros,
                "PRO_12",
                "ROE",
                value,
                period,
                f"Positive return on equity of {value:.2f}%.",
            )

    return pros


# ============================================================
# 12 CON RULES
# ============================================================

def generate_cons(
    metric_type,
    value,
    period,
):
    """Generate negative signals using 12 explicit rules."""

    cons = []

    if not valid(value):
        return cons

    value = float(value)

    # --------------------------------------------------------
    # REVENUE CAGR - 3 CON RULES
    # --------------------------------------------------------

    if metric_type == "revenue_cagr":

        if value < 0:
            add_signal(
                cons,
                "CON_01",
                "Revenue CAGR",
                value,
                period,
                f"Revenue contracted by {abs(value):.2f}%.",
            )

        elif 0 <= value < 3:
            add_signal(
                cons,
                "CON_02",
                "Revenue CAGR",
                value,
                period,
                f"Revenue growth is weak at {value:.2f}%.",
            )

        elif 3 <= value < 5:
            add_signal(
                cons,
                "CON_03",
                "Revenue CAGR",
                value,
                period,
                f"Revenue growth is modest at {value:.2f}%.",
            )

    # --------------------------------------------------------
    # PAT CAGR - 3 CON RULES
    # --------------------------------------------------------

    elif metric_type == "pat_cagr":

        if value < 0:
            add_signal(
                cons,
                "CON_04",
                "PAT CAGR",
                value,
                period,
                f"Profit contracted by {abs(value):.2f}%.",
            )

        elif 0 <= value < 3:
            add_signal(
                cons,
                "CON_05",
                "PAT CAGR",
                value,
                period,
                f"Profit growth is weak at {value:.2f}%.",
            )

        elif 3 <= value < 5:
            add_signal(
                cons,
                "CON_06",
                "PAT CAGR",
                value,
                period,
                f"Profit growth is modest at {value:.2f}%.",
            )

    # --------------------------------------------------------
    # STOCK PRICE CAGR - 3 CON RULES
    # --------------------------------------------------------

    elif metric_type == "stock_price_cagr":

        if value < 0:
            add_signal(
                cons,
                "CON_07",
                "Stock Price CAGR",
                value,
                period,
                f"Stock-price CAGR is negative at {value:.2f}%.",
            )

        elif 0 <= value < 3:
            add_signal(
                cons,
                "CON_08",
                "Stock Price CAGR",
                value,
                period,
                f"Stock-price CAGR is weak at {value:.2f}%.",
            )

        elif 3 <= value < 5:
            add_signal(
                cons,
                "CON_09",
                "Stock Price CAGR",
                value,
                period,
                f"Stock-price CAGR is modest at {value:.2f}%.",
            )

    # --------------------------------------------------------
    # ROE - 3 CON RULES
    # --------------------------------------------------------

    elif metric_type == "roe":

        if value < 5:
            add_signal(
                cons,
                "CON_10",
                "ROE",
                value,
                period,
                f"Return on equity is very low at {value:.2f}%.",
            )

        elif 5 <= value < 8:
            add_signal(
                cons,
                "CON_11",
                "ROE",
                value,
                period,
                f"Return on equity is weak at {value:.2f}%.",
            )

        elif 8 <= value < 10:
            add_signal(
                cons,
                "CON_12",
                "ROE",
                value,
                period,
                f"Return on equity is below 10% at {value:.2f}%.",
            )

    return cons


# ============================================================
# GENERATOR
# ============================================================

def generate_pros_cons():
    """
    Generate Pros and Cons from normalized Day 29 data.

    Each normalized financial metric is evaluated against
    the 12 Pro and 12 Con rules.
    """

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Parsed analysis file not found: {INPUT_PATH}"
        )

    frame = pd.read_csv(
        INPUT_PATH
    )

    required_columns = {
        "company_id",
        "metric_type",
        "period_years",
        "value_pct",
    }

    missing = (
        required_columns
        - set(frame.columns)
    )

    if missing:
        raise ValueError(
            "Missing required parsed-analysis columns: "
            + ", ".join(sorted(missing))
        )

    signal_rows = []

    for _, row in frame.iterrows():

        company_id = str(
            row["company_id"]
        ).strip()

        metric_type = str(
            row["metric_type"]
        ).strip()

        value = row["value_pct"]

        period = period_label(
            row["period_years"]
        )

        pros = generate_pros(
            metric_type,
            value,
            period,
        )

        cons = generate_cons(
            metric_type,
            value,
            period,
        )

        for signal in pros:

            signal_rows.append(
                {
                    "company_id":
                        company_id,

                    "signal_type":
                        "PRO",

                    "rule_id":
                        signal["rule_id"],

                    "metric":
                        signal["metric"],

                    "period":
                        signal["period"],

                    "value_pct":
                        signal["value_pct"],

                    "message":
                        signal["message"],
                }
            )

        for signal in cons:

            signal_rows.append(
                {
                    "company_id":
                        company_id,

                    "signal_type":
                        "CON",

                    "rule_id":
                        signal["rule_id"],

                    "metric":
                        signal["metric"],

                    "period":
                        signal["period"],

                    "value_pct":
                        signal["value_pct"],

                    "message":
                        signal["message"],
                }
            )

    return pd.DataFrame(
        signal_rows,
        columns=[
            "company_id",
            "signal_type",
            "rule_id",
            "metric",
            "period",
            "value_pct",
            "message",
        ],
    )


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_pros_cons(frame):
    """Save Day 30 generated Pros and Cons."""

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    frame.to_csv(
        OUTPUT_PATH,
        index=False,
    )


# ============================================================
# QA
# ============================================================

def print_rule_coverage(frame):
    """Print Day 30 rule coverage."""

    if frame.empty:

        print(
            "NO PRO / CON SIGNALS GENERATED"
        )

        return

    pro_rows = frame[
        frame["signal_type"] == "PRO"
    ]

    con_rows = frame[
        frame["signal_type"] == "CON"
    ]

    print(
        "TOTAL SIGNALS:",
        len(frame),
    )

    print(
        "TOTAL PRO SIGNALS:",
        len(pro_rows),
    )

    print(
        "TOTAL CON SIGNALS:",
        len(con_rows),
    )

    print(
        "COMPANIES:",
        frame["company_id"].nunique(),
    )

    print(
        "\nPRO RULES TRIGGERED:"
    )

    triggered_pros = sorted(
        pro_rows["rule_id"]
        .dropna()
        .unique()
        .tolist()
    )

    if triggered_pros:
        print(
            ", ".join(triggered_pros)
        )
    else:
        print("NONE")

    print(
        "\nCON RULES TRIGGERED:"
    )

    triggered_cons = sorted(
        con_rows["rule_id"]
        .dropna()
        .unique()
        .tolist()
    )

    if triggered_cons:
        print(
            ", ".join(triggered_cons)
        )
    else:
        print("NONE")

    print(
        "\nRULES IMPLEMENTED:"
    )

    print(
        "PRO RULES: 12"
    )

    print(
        "CON RULES: 12"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    output = generate_pros_cons()

    save_pros_cons(
        output
    )

    print(
        "DAY 30 PROS / CONS GENERATOR COMPLETE"
    )

    print_rule_coverage(
        output
    )

    print(
        "\nOUTPUT:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()