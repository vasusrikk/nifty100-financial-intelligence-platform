"""Sprint 2 - Day 13 Bank ROCE Carve-Out & Edge Case Log."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


DB_PATH = Path("nifty100.db")
OUTPUT = Path("output/ratio_edge_cases.log")

ROCE_TOLERANCE = 5.0
ROE_TOLERANCE = 5.0


def to_float(value) -> Optional[float]:
    """Convert database value to float safely."""

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def classify_anomaly(
    calculated: Optional[float],
    source: Optional[float],
    difference: Optional[float],
) -> str:
    """
    Categorize an anomaly for the Day 13 review log.

    This is a diagnostic category, not a claim that the source
    or calculated value is necessarily incorrect.
    """

    if calculated is None or source is None:
        return "DATA_SOURCE_ISSUE"

    # Extremely different values can indicate a scale/unit/source issue.
    if (
        abs(source) < 1
        and abs(calculated) >= 5
    ):
        return "DATA_SOURCE_ISSUE"

    if difference is not None and difference <= 10:
        return "VERSION_DIFFERENCE"

    return "FORMULA_DISCREPANCY"


def load_ratio_comparison(
    connection: sqlite3.Connection,
):
    """Load calculated ratios with source ROE/ROCE and sector."""

    query = """
        SELECT
            fr.company_id,
            c.company_name,
            fr.year,
            s.broad_sector,

            fr.roe_pct AS calculated_roe,
            c.roe_percentage AS source_roe,

            fr.roce_pct AS calculated_roce,
            c.roce_percentage AS source_roce,

            fr.de_ratio,
            fr.leverage_flag

        FROM financial_ratios fr

        JOIN companies c
            ON c.id = fr.company_id

        LEFT JOIN sectors s
            ON s.company_id = fr.company_id

        ORDER BY
            c.company_name,
            fr.year
    """

    return connection.execute(query).fetchall()


def generate_edge_case_log() -> None:
    """Generate the Sprint 2 Day 13 edge-case review log."""

    connection = sqlite3.connect(DB_PATH)

    try:
        rows = load_ratio_comparison(connection)

    finally:
        connection.close()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    financial_rows = 0
    financial_carveout_rows = 0

    roce_anomalies = 0
    roe_anomalies = 0

    category_counts = {
        "DATA_SOURCE_ISSUE": 0,
        "VERSION_DIFFERENCE": 0,
        "FORMULA_DISCREPANCY": 0,
    }

    lines = []

    lines.append(
        "SPRINT 2 - DAY 13 RATIO EDGE CASE REVIEW"
    )
    lines.append("=" * 72)

    lines.append("")
    lines.append(
        "Policy: calculated ratio-engine values are used for analytics."
    )
    lines.append(
        "Source ROE/ROCE values are retained only for cross-validation."
    )

    lines.append("")
    lines.append(
        "Financial-sector D/E policy: standard leverage warnings are "
        "suppressed because structurally high leverage is normal for "
        "banks/NBFCs/insurance companies."
    )

    lines.append("")
    lines.append("=" * 72)
    lines.append("FINANCIAL-SECTOR D/E CARVE-OUT")
    lines.append("=" * 72)

    for row in rows:

        (
            company_id,
            company_name,
            year,
            broad_sector,
            calculated_roe,
            source_roe,
            calculated_roce,
            source_roce,
            de_ratio,
            leverage_flag,
        ) = row

        is_financial = (
            broad_sector is not None
            and str(broad_sector).strip().lower()
            == "financials"
        )

        if not is_financial:
            continue

        financial_rows += 1

        if leverage_flag == "SECTOR_RELATIVE":
            financial_carveout_rows += 1

        lines.append(
            f"{company_id} | {company_name} | {year} | "
            f"D/E={de_ratio} | flag={leverage_flag}"
        )

    lines.append("")
    lines.append("=" * 72)
    lines.append("ROCE CROSS-CHECK ANOMALIES (> 5 percentage points)")
    lines.append("=" * 72)

    for row in rows:

        (
            company_id,
            company_name,
            year,
            broad_sector,
            calculated_roe,
            source_roe,
            calculated_roce,
            source_roce,
            de_ratio,
            leverage_flag,
        ) = row

        calc = to_float(calculated_roce)
        source = to_float(source_roce)

        if calc is None or source is None:
            continue

        difference = abs(calc - source)

        if difference <= ROCE_TOLERANCE:
            continue

        category = classify_anomaly(
            calc,
            source,
            difference,
        )

        category_counts[category] += 1
        roce_anomalies += 1

        lines.append(
            f"{company_id} | {company_name} | {year} | "
            f"sector={broad_sector} | "
            f"calculated_ROCE={calc:.4f}% | "
            f"source_ROCE={source:.4f}% | "
            f"difference={difference:.4f} pp | "
            f"category={category}"
        )

    lines.append("")
    lines.append("=" * 72)
    lines.append("ROE CROSS-CHECK ANOMALIES (> 5 percentage points)")
    lines.append("=" * 72)

    for row in rows:

        (
            company_id,
            company_name,
            year,
            broad_sector,
            calculated_roe,
            source_roe,
            calculated_roce,
            source_roce,
            de_ratio,
            leverage_flag,
        ) = row

        calc = to_float(calculated_roe)
        source = to_float(source_roe)

        if calc is None or source is None:
            continue

        difference = abs(calc - source)

        if difference <= ROE_TOLERANCE:
            continue

        category = classify_anomaly(
            calc,
            source,
            difference,
        )

        category_counts[category] += 1
        roe_anomalies += 1

        lines.append(
            f"{company_id} | {company_name} | {year} | "
            f"sector={broad_sector} | "
            f"calculated_ROE={calc:.4f}% | "
            f"source_ROE={source:.4f}% | "
            f"difference={difference:.4f} pp | "
            f"category={category}"
        )

    lines.append("")
    lines.append("=" * 72)
    lines.append("DAY 13 SUMMARY")
    lines.append("=" * 72)

    lines.append(
        f"Financial-sector company-year rows: {financial_rows}"
    )

    lines.append(
        f"Financial-sector rows using D/E carve-out: "
        f"{financial_carveout_rows}"
    )

    lines.append(
        f"ROCE anomalies > 5 pp: {roce_anomalies}"
    )

    lines.append(
        f"ROE anomalies > 5 pp: {roe_anomalies}"
    )

    lines.append("")
    lines.append("Anomaly categories:")

    for category, count in category_counts.items():
        lines.append(
            f"  {category}: {count}"
        )

    lines.append("")
    lines.append(
        "NOTE: Source company-level ROE/ROCE values do not contain "
        "a year dimension. They are therefore used only as reference "
        "cross-check values against company-year calculated ratios."
    )

    lines.append(
        "Calculated financial_ratios values remain authoritative "
        "for analytics."
    )

    OUTPUT.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(
        "\n=== SPRINT 2 - DAY 13 "
        "BANK ROCE CARVE-OUT & EDGE CASE REVIEW ==="
    )

    print(
        "Financial-sector company-year rows:",
        financial_rows,
    )

    print(
        "D/E carve-out rows:",
        financial_carveout_rows,
    )

    print(
        "ROCE anomalies > 5 pp:",
        roce_anomalies,
    )

    print(
        "ROE anomalies > 5 pp:",
        roe_anomalies,
    )

    print("\nAnomaly categories:")

    for category, count in category_counts.items():
        print(
            f"{category:<22}: {count}"
        )

    print("\nSaved:", OUTPUT)


def main() -> None:
    generate_edge_case_log()


if __name__ == "__main__":
    main()