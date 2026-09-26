"""Sprint 3 - Day 16: Preset Screeners."""

from __future__ import annotations

import sqlite3

from src.screener.engine import (
    apply_filters,
    load_screener_data,
)


# ============================================================
# HISTORICAL HELPERS
# ============================================================

def get_revenue_cagr_3yr(
    company_id,
    db_path="nifty100.db",
):
    """
    Calculate 3-year revenue CAGR using actual fiscal-year
    endpoints from profitandloss.
    """

    connection = sqlite3.connect(db_path)

    try:
        rows = connection.execute(
            """
            SELECT year, sales
            FROM profitandloss
            WHERE company_id = ?
              AND sales IS NOT NULL
            ORDER BY year DESC
            """,
            (company_id,),
        ).fetchall()

    finally:
        connection.close()

    if not rows:
        return None

    latest_year = rows[0][0]
    latest_sales = rows[0][1]

    try:
        latest_fy = int(latest_year[:4])
    except (TypeError, ValueError):
        return None

    target_fy = latest_fy - 3

    old_sales = None

    for year, sales in rows:
        try:
            fy = int(year[:4])
        except (TypeError, ValueError):
            continue

        if fy == target_fy:
            old_sales = sales
            break

    if (
        old_sales is None
        or latest_sales is None
        or old_sales <= 0
        or latest_sales <= 0
    ):
        return None

    return (
        (latest_sales / old_sales) ** (1 / 3)
        - 1
    ) * 100


def is_de_declining(
    company_id,
    db_path="nifty100.db",
):
    """
    Check whether latest D/E is lower than the immediately
    preceding usable D/E observation.
    """

    connection = sqlite3.connect(db_path)

    try:
        rows = connection.execute(
            """
            SELECT year, de_ratio
            FROM financial_ratios
            WHERE company_id = ?
              AND de_ratio IS NOT NULL
            ORDER BY year DESC
            LIMIT 2
            """,
            (company_id,),
        ).fetchall()

    finally:
        connection.close()

    if len(rows) < 2:
        return False

    latest_de = rows[0][1]
    previous_de = rows[1][1]

    return latest_de < previous_de


# ============================================================
# PRESET DEFINITIONS
# ============================================================

PRESETS = {
    "quality_compounder": {
        "name": "Quality Compounder",
        "filters": [
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 15,
            },
            {
                "metric": "de_ratio",
                "operator": "<",
                "value": 1.0,
            },
            {
                "metric": "revenue_cagr_5yr",
                "operator": ">",
                "value": 10,
            },
        ],
        "requires_fcf": True,
    },

    "value_pick": {
        "name": "Value Pick",
        "filters": [
            {
                "metric": "pe_ratio",
                "operator": "<",
                "value": 20,
            },
            {
                "metric": "pb_ratio",
                "operator": "<",
                "value": 3.0,
            },
            {
                "metric": "de_ratio",
                "operator": "<",
                "value": 2.0,
            },
            {
                "metric": "dividend_yield_pct",
                "operator": ">",
                "value": 1,
            },
        ],
        "requires_fcf": False,
    },

    "growth_accelerator": {
        "name": "Growth Accelerator",
        "filters": [
            {
                "metric": "pat_cagr_5yr",
                "operator": ">",
                "value": 20,
            },
            {
                "metric": "revenue_cagr_5yr",
                "operator": ">",
                "value": 15,
            },
            {
                "metric": "de_ratio",
                "operator": "<",
                "value": 2.0,
            },
        ],
        "requires_fcf": False,
    },

    "dividend_champion": {
        "name": "Dividend Champion",
        "filters": [
            {
                "metric": "dividend_yield_pct",
                "operator": ">",
                "value": 2,
            },
        ],
        "requires_fcf": True,
        "requires_dividend_payout": True,
    },

    "debt_free_blue_chip": {
        "name": "Debt-Free Blue Chip",
        "filters": [
            {
                "metric": "de_ratio",
                "operator": "==",
                "value": 0,
            },
            {
                "metric": "roe_pct",
                "operator": ">",
                "value": 12,
            },
        ],
        "requires_fcf": False,
        "requires_revenue": True,
    },

    "turnaround_watch": {
        "name": "Turnaround Watch",
        "filters": [],
        "requires_fcf": True,
        "requires_revenue_cagr_3yr": True,
        "requires_de_declining": True,
    },
}


# ============================================================
# PRESET RUNNER
# ============================================================

def run_preset(
    preset_key,
    rows=None,
):
    if preset_key not in PRESETS:
        raise ValueError(
            f"Unknown preset: {preset_key}"
        )

    if rows is None:
        rows = load_screener_data()

    preset = PRESETS[preset_key]

    result = apply_filters(
        rows,
        preset["filters"],
    )

    # --------------------------------------------------------
    # DEBT-FREE BLUE CHIP:
    # Explicit D/E = 0 must be enforced even for Financials.
    # The generic Financial-sector D/E carve-out does not
    # apply to an explicitly debt-free preset.
    # --------------------------------------------------------

    if preset_key == "debt_free_blue_chip":
        result = [
            row
            for row in result
            if (
                row.get("de_ratio") is not None
                and float(row["de_ratio"]) == 0.0
            )
        ]

    # --------------------------------------------------------
    # DIVIDEND PAYOUT < 80%
    # --------------------------------------------------------

    if preset.get("requires_dividend_payout"):
        result = [
            row
            for row in result
            if (
                row.get("dividend_payout") is not None
                and row["dividend_payout"] < 80
            )
        ]

    # --------------------------------------------------------
    # REVENUE > 5000 CRORE
    # --------------------------------------------------------

    if preset.get("requires_revenue"):
        result = [
            row
            for row in result
            if (
                row.get("sales") is not None
                and row["sales"] > 5000
            )
        ]

    # --------------------------------------------------------
    # 3-YEAR REVENUE CAGR > 10%
    # --------------------------------------------------------

    if preset.get("requires_revenue_cagr_3yr"):

        filtered = []

        for row in result:

            cagr = get_revenue_cagr_3yr(
                row["company_id"]
            )

            if (
                cagr is not None
                and cagr > 10
            ):
                row = dict(row)
                row["revenue_cagr_3yr"] = cagr
                filtered.append(row)

        result = filtered

    # --------------------------------------------------------
    # DECLINING D/E
    # --------------------------------------------------------

    if preset.get("requires_de_declining"):
        result = [
            row
            for row in result
            if is_de_declining(
                row["company_id"]
            )
        ]

    # --------------------------------------------------------
    # FCF > 0
    #
    # Current database has no explicit Capex source, therefore
    # FCF cannot be evaluated honestly.
    # --------------------------------------------------------

    if preset.get("requires_fcf"):

        fcf_available = any(
            row.get("fcf") is not None
            for row in rows
        )

        if not fcf_available:
            return {
                "preset": preset["name"],
                "status": "SOURCE_LIMITATION",
                "reason": (
                    "FCF condition cannot be evaluated because "
                    "explicit Capex source is unavailable."
                ),
                "partial_results": result,
            }

        result = [
            row
            for row in result
            if (
                row.get("fcf") is not None
                and row["fcf"] > 0
            )
        ]

    return {
        "preset": preset["name"],
        "status": "COMPLETE",
        "results": result,
    }
    # FCF requirement cannot currently be evaluated because
    # Sprint 2 has no explicit Capex source.
    if preset.get("requires_fcf"):

        fcf_available = any(
            row.get("fcf") is not None
            for row in rows
        )

        if not fcf_available:
            return {
                "preset": preset["name"],
                "status": "SOURCE_LIMITATION",
                "reason": (
                    "FCF condition cannot be evaluated because "
                    "explicit Capex source is unavailable."
                ),
                "partial_results": result,
            }

        result = [
            row
            for row in result
            if (
                row.get("fcf") is not None
                and row["fcf"] > 0
            )
        ]

    return {
        "preset": preset["name"],
        "status": "COMPLETE",
        "results": result,
    }


# ============================================================
# DAY 16 QA
# ============================================================

def main():

    rows = load_screener_data()

    print(
        "\n=== SPRINT 3 - DAY 16 "
        "PRESET SCREENER QA ==="
    )

    print(
        "Universe:",
        len(rows),
        "companies",
    )

    for key in PRESETS:

        output = run_preset(
            key,
            rows,
        )

        print(
            "\n",
            output["preset"],
            sep="",
        )

        print(
            "Status:",
            output["status"],
        )

        if output["status"] == "COMPLETE":

            results = output["results"]

            print(
                "Companies:",
                len(results),
            )

        else:

            results = output[
                "partial_results"
            ]

            print(
                "Partial candidates:",
                len(results),
            )

            print(
                "Reason:",
                output["reason"],
            )


if __name__ == "__main__":
    main()