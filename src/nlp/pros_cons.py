"""Day 29 - Automatic Pros and Cons Generator."""

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
    """Add one generated signal."""

    signals.append(
        {
            "rule_id": rule_id,
            "metric": metric,
            "period": period,
            "value_pct": value,
            "message": message,
        }
    )


# ============================================================
# 12 PRO RULES
# ============================================================

def generate_pros(row):
    """Generate positive signals using 12 explicit rules."""

    pros = []

    sales = row.get("sales_growth_pct")
    sales_period = row.get("sales_growth_period")

    profit = row.get("profit_growth_pct")
    profit_period = row.get("profit_growth_period")

    stock = row.get("stock_price_cagr_pct")
    stock_period = row.get("stock_price_cagr_period")

    roe = row.get("roe_pct")
    roe_period = row.get("roe_period")


    # --------------------------------------------------------
    # SALES GROWTH - 3 PRO RULES
    # --------------------------------------------------------

    if valid(sales) and sales >= 20:
        add_signal(
            pros,
            "PRO_01",
            "Sales Growth",
            sales,
            sales_period,
            f"Excellent sales growth of {sales:.2f}%.",
        )

    if (
        valid(sales)
        and 10 <= sales < 20
    ):
        add_signal(
            pros,
            "PRO_02",
            "Sales Growth",
            sales,
            sales_period,
            f"Healthy sales growth of {sales:.2f}%.",
        )

    if (
        valid(sales)
        and 5 <= sales < 10
    ):
        add_signal(
            pros,
            "PRO_03",
            "Sales Growth",
            sales,
            sales_period,
            f"Positive sales growth of {sales:.2f}%.",
        )


    # --------------------------------------------------------
    # PROFIT GROWTH - 3 PRO RULES
    # --------------------------------------------------------

    if valid(profit) and profit >= 20:
        add_signal(
            pros,
            "PRO_04",
            "Profit Growth",
            profit,
            profit_period,
            f"Excellent profit growth of {profit:.2f}%.",
        )

    if (
        valid(profit)
        and 10 <= profit < 20
    ):
        add_signal(
            pros,
            "PRO_05",
            "Profit Growth",
            profit,
            profit_period,
            f"Healthy profit growth of {profit:.2f}%.",
        )

    if (
        valid(profit)
        and 5 <= profit < 10
    ):
        add_signal(
            pros,
            "PRO_06",
            "Profit Growth",
            profit,
            profit_period,
            f"Positive profit growth of {profit:.2f}%.",
        )


    # --------------------------------------------------------
    # STOCK PRICE CAGR - 3 PRO RULES
    # --------------------------------------------------------

    if valid(stock) and stock >= 20:
        add_signal(
            pros,
            "PRO_07",
            "Stock Price CAGR",
            stock,
            stock_period,
            f"Strong stock-price CAGR of {stock:.2f}%.",
        )

    if (
        valid(stock)
        and 10 <= stock < 20
    ):
        add_signal(
            pros,
            "PRO_08",
            "Stock Price CAGR",
            stock,
            stock_period,
            f"Healthy stock-price CAGR of {stock:.2f}%.",
        )

    if (
        valid(stock)
        and 5 <= stock < 10
    ):
        add_signal(
            pros,
            "PRO_09",
            "Stock Price CAGR",
            stock,
            stock_period,
            f"Positive stock-price CAGR of {stock:.2f}%.",
        )


    # --------------------------------------------------------
    # ROE - 3 PRO RULES
    # --------------------------------------------------------

    if valid(roe) and roe >= 25:
        add_signal(
            pros,
            "PRO_10",
            "ROE",
            roe,
            roe_period,
            f"Excellent return on equity of {roe:.2f}%.",
        )

    if (
        valid(roe)
        and 15 <= roe < 25
    ):
        add_signal(
            pros,
            "PRO_11",
            "ROE",
            roe,
            roe_period,
            f"Healthy return on equity of {roe:.2f}%.",
        )

    if (
        valid(roe)
        and 10 <= roe < 15
    ):
        add_signal(
            pros,
            "PRO_12",
            "ROE",
            roe,
            roe_period,
            f"Positive return on equity of {roe:.2f}%.",
        )

    return pros


# ============================================================
# 12 CON RULES
# ============================================================

def generate_cons(row):
    """Generate negative signals using 12 explicit rules."""

    cons = []

    sales = row.get("sales_growth_pct")
    sales_period = row.get("sales_growth_period")

    profit = row.get("profit_growth_pct")
    profit_period = row.get("profit_growth_period")

    stock = row.get("stock_price_cagr_pct")
    stock_period = row.get("stock_price_cagr_period")

    roe = row.get("roe_pct")
    roe_period = row.get("roe_period")


    # --------------------------------------------------------
    # SALES GROWTH - 3 CON RULES
    # --------------------------------------------------------

    if valid(sales) and sales < 0:
        add_signal(
            cons,
            "CON_01",
            "Sales Growth",
            sales,
            sales_period,
            f"Sales contracted by {abs(sales):.2f}%.",
        )

    if (
        valid(sales)
        and 0 <= sales < 3
    ):
        add_signal(
            cons,
            "CON_02",
            "Sales Growth",
            sales,
            sales_period,
            f"Sales growth is weak at {sales:.2f}%.",
        )

    if (
        valid(sales)
        and 3 <= sales < 5
    ):
        add_signal(
            cons,
            "CON_03",
            "Sales Growth",
            sales,
            sales_period,
            f"Sales growth is modest at {sales:.2f}%.",
        )


    # --------------------------------------------------------
    # PROFIT GROWTH - 3 CON RULES
    # --------------------------------------------------------

    if valid(profit) and profit < 0:
        add_signal(
            cons,
            "CON_04",
            "Profit Growth",
            profit,
            profit_period,
            f"Profit contracted by {abs(profit):.2f}%.",
        )

    if (
        valid(profit)
        and 0 <= profit < 3
    ):
        add_signal(
            cons,
            "CON_05",
            "Profit Growth",
            profit,
            profit_period,
            f"Profit growth is weak at {profit:.2f}%.",
        )

    if (
        valid(profit)
        and 3 <= profit < 5
    ):
        add_signal(
            cons,
            "CON_06",
            "Profit Growth",
            profit,
            profit_period,
            f"Profit growth is modest at {profit:.2f}%.",
        )


    # --------------------------------------------------------
    # STOCK PRICE CAGR - 3 CON RULES
    # --------------------------------------------------------

    if valid(stock) and stock < 0:
        add_signal(
            cons,
            "CON_07",
            "Stock Price CAGR",
            stock,
            stock_period,
            f"Stock-price CAGR is negative at {stock:.2f}%.",
        )

    if (
        valid(stock)
        and 0 <= stock < 3
    ):
        add_signal(
            cons,
            "CON_08",
            "Stock Price CAGR",
            stock,
            stock_period,
            f"Stock-price CAGR is weak at {stock:.2f}%.",
        )

    if (
        valid(stock)
        and 3 <= stock < 5
    ):
        add_signal(
            cons,
            "CON_09",
            "Stock Price CAGR",
            stock,
            stock_period,
            f"Stock-price CAGR is modest at {stock:.2f}%.",
        )


    # --------------------------------------------------------
    # ROE - 3 CON RULES
    # --------------------------------------------------------

    if valid(roe) and roe < 5:
        add_signal(
            cons,
            "CON_10",
            "ROE",
            roe,
            roe_period,
            f"Return on equity is very low at {roe:.2f}%.",
        )

    if (
        valid(roe)
        and 5 <= roe < 8
    ):
        add_signal(
            cons,
            "CON_11",
            "ROE",
            roe,
            roe_period,
            f"Return on equity is weak at {roe:.2f}%.",
        )

    if (
        valid(roe)
        and 8 <= roe < 10
    ):
        add_signal(
            cons,
            "CON_12",
            "ROE",
            roe,
            roe_period,
            f"Return on equity is below 10% at {roe:.2f}%.",
        )

    return cons


# ============================================================
# GENERATE OUTPUT
# ============================================================

def generate_pros_cons():
    """Generate Pros and Cons for every parsed analysis row."""

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Parsed analysis file not found: {INPUT_PATH}"
        )

    frame = pd.read_csv(
        INPUT_PATH
    )

    output_rows = []

    for _, row in frame.iterrows():

        pros = generate_pros(
            row
        )

        cons = generate_cons(
            row
        )

        output_rows.append(
            {
                "id":
                    row.get("id"),

                "company_id":
                    row.get("company_id"),

                "pros_count":
                    len(pros),

                "cons_count":
                    len(cons),

                "pros":
                    " | ".join(
                        item["message"]
                        for item in pros
                    ),

                "cons":
                    " | ".join(
                        item["message"]
                        for item in cons
                    ),

                "pro_rule_ids":
                    ", ".join(
                        item["rule_id"]
                        for item in pros
                    ),

                "con_rule_ids":
                    ", ".join(
                        item["rule_id"]
                        for item in cons
                    ),
            }
        )

    return pd.DataFrame(
        output_rows
    )


# ============================================================
# EXPORT
# ============================================================

def save_pros_cons(frame):
    """Save generated Pros and Cons."""

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    frame.to_csv(
        OUTPUT_PATH,
        index=False,
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
        "PROS / CONS GENERATOR COMPLETE"
    )

    print(
        "ROWS:",
        len(output),
    )

    print(
        "COMPANIES:",
        output[
            "company_id"
        ].nunique(),
    )

    print(
        "TOTAL PRO SIGNALS:",
        int(
            output[
                "pros_count"
            ].sum()
        ),
    )

    print(
        "TOTAL CON SIGNALS:",
        int(
            output[
                "cons_count"
            ].sum()
        ),
    )

    print(
        "PRO RULES IMPLEMENTED: 12"
    )

    print(
        "CON RULES IMPLEMENTED: 12"
    )

    print(
        "OUTPUT:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()