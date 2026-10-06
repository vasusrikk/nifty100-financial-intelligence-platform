"""Generate NIFTY 100 broad-sector PDF reports."""

from __future__ import annotations

import math
import sqlite3
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "sector"


def safe_number(value, decimals=2):
    """Return a display-safe numeric value."""
    if value is None:
        return "N/A"

    try:
        number = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if not math.isfinite(number):
        return "N/A"

    return f"{number:.{decimals}f}"


def safe_filename(value):
    """Convert sector name to a safe PDF filename."""
    return "".join(
        ch if ch.isalnum() or ch in "-_" else "_"
        for ch in str(value)
    )


def load_sector_data():
    """Load the latest financial snapshot for all companies."""

    connection = sqlite3.connect(DATABASE_PATH)

    query = """
    WITH latest_ratios AS (
        SELECT fr.*
        FROM financial_ratios fr
        INNER JOIN (
            SELECT company_id, MAX(year) AS max_year
            FROM financial_ratios
            GROUP BY company_id
        ) latest
            ON latest.company_id = fr.company_id
           AND latest.max_year = fr.year
    ),
    latest_market AS (
        SELECT mc.*
        FROM market_cap mc
        INNER JOIN (
            SELECT company_id, MAX(year) AS max_year
            FROM market_cap
            GROUP BY company_id
        ) latest
            ON latest.company_id = mc.company_id
           AND latest.max_year = mc.year
    )
    SELECT
        c.id AS company_id,
        c.company_name,
        s.broad_sector,
        s.sub_sector,
        s.index_weight_pct,
        fr.year,
        fr.roe_pct,
        fr.roce_pct,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.cfo_margin_pct,
        fr.de_ratio,
        mc.market_cap_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct
    FROM companies c
    JOIN sectors s
        ON s.company_id = c.id
    LEFT JOIN latest_ratios fr
        ON fr.company_id = c.id
    LEFT JOIN latest_market mc
        ON mc.company_id = c.id
    ORDER BY
        s.broad_sector,
        c.company_name
    """

    try:
        cursor = connection.execute(query)
        columns = [item[0] for item in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    finally:
        connection.close()


def median(values):
    """Calculate median while excluding unavailable values."""

    clean = []

    for value in values:
        if value is None:
            continue

        try:
            value = float(value)
        except (TypeError, ValueError):
            continue

        if math.isfinite(value):
            clean.append(value)

    if not clean:
        return None

    clean.sort()
    n = len(clean)
    middle = n // 2

    if n % 2:
        return clean[middle]

    return (
        clean[middle - 1] + clean[middle]
    ) / 2


def build_sector_summary(rows):
    """Calculate transparent sector-level summary statistics."""

    return {
        "companies": len(rows),
        "index_weight": sum(
            float(row["index_weight_pct"] or 0)
            for row in rows
        ),
        "median_roe": median(
            row["roe_pct"] for row in rows
        ),
        "median_roce": median(
            row["roce_pct"] for row in rows
        ),
        "median_revenue_growth": median(
            row["revenue_cagr_5yr"] for row in rows
        ),
        "median_pat_growth": median(
            row["pat_cagr_5yr"] for row in rows
        ),
        "median_cfo_margin": median(
            row["cfo_margin_pct"] for row in rows
        ),
        "median_de": median(
            row["de_ratio"] for row in rows
        ),
        "median_pe": median(
            row["pe_ratio"] for row in rows
        ),
        "median_pb": median(
            row["pb_ratio"] for row in rows
        ),
    }
def generate_all_sectors_summary(grouped):
    """Generate an aggregate comparison report for all broad sectors."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = OUTPUT_DIR / "All_Sectors_Summary.pdf"

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "AllSectorsTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "AllSectorsHeading",
        parent=styles["Heading2"],
        spaceBefore=8,
        spaceAfter=8,
    )

    body_style = styles["BodyText"]

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    story = []

    story.append(
        Paragraph(
            "NIFTY 100 - All Sectors Summary",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Aggregate comparison of all broad sectors represented "
            "in the NIFTY 100 financial intelligence dataset.",
            body_style,
        )
    )

    story.append(Spacer(1, 10))

    total_companies = sum(
        len(rows) for rows in grouped.values()
    )

    story.append(
        Paragraph(
            f"<b>Total Broad Sectors:</b> {len(grouped)}"
            f"<br/><b>Total Companies:</b> {total_companies}",
            body_style,
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Sector Comparison",
            heading_style,
        )
    )

    table_data = [
        [
            "Sector",
            "Companies",
            "Index Weight %",
            "Median ROE %",
            "Median ROCE %",
            "Median P/E",
        ]
    ]

    for sector in sorted(grouped):
        summary = build_sector_summary(
            grouped[sector]
        )

        table_data.append(
            [
                sector,
                str(summary["companies"]),
                safe_number(summary["index_weight"]),
                safe_number(summary["median_roe"]),
                safe_number(summary["median_roce"]),
                safe_number(summary["median_pe"]),
            ]
        )

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            47 * mm,
            20 * mm,
            28 * mm,
            25 * mm,
            27 * mm,
            25 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, 0),
                    7,
                ),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "This summary consolidates the ten broad-sector reports "
            "into one cross-sector comparison. It does not introduce "
            "an additional sector or fabricate sector-level data.",
            body_style,
        )
    )

    document.build(story)

    return output_path














def generate_sector_report(sector, rows):
    """Generate one PDF for a broad sector."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / f"{safe_filename(sector)}.pdf"
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=f"{sector} Sector Report",
        author="Nifty 100 Financial Intelligence Platform",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "SectorTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "SectorSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#555555"),
        spaceAfter=14,
    )

    heading_style = ParagraphStyle(
        "SectorHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=8,
        spaceAfter=7,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=9,
    )

    story = []

    story.append(
        Paragraph(
            f"NIFTY 100 — {sector}",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Sector Intelligence Report",
            subtitle_style,
        )
    )

    summary = build_sector_summary(rows)

    story.append(
        Paragraph(
            "Sector Snapshot",
            heading_style,
        )
    )

    snapshot_data = [
        ["Metric", "Sector Value"],
        ["Companies", str(summary["companies"])],
        [
            "Index Weight (%)",
            safe_number(summary["index_weight"]),
        ],
        [
            "Median ROE (%)",
            safe_number(summary["median_roe"]),
        ],
        [
            "Median ROCE (%)",
            safe_number(summary["median_roce"]),
        ],
        [
            "Median Revenue CAGR (%)",
            safe_number(
                summary["median_revenue_growth"]
            ),
        ],
        [
            "Median PAT CAGR (%)",
            safe_number(
                summary["median_pat_growth"]
            ),
        ],
        [
            "Median CFO Margin (%)",
            safe_number(
                summary["median_cfo_margin"]
            ),
        ],
        [
            "Median D/E",
            safe_number(summary["median_de"]),
        ],
        [
            "Median P/E",
            safe_number(summary["median_pe"]),
        ],
        [
            "Median P/B",
            safe_number(summary["median_pb"]),
        ],
    ]

    snapshot_table = Table(
        snapshot_data,
        colWidths=[80 * mm, 70 * mm],
        repeatRows=1,
    )

    snapshot_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#E5E7EB"),
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.35,
                colors.HexColor("#BDBDBD"),
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8.5,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F8F9FA"),
                ],
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
        ])
    )

    story.append(snapshot_table)
    story.append(Spacer(1, 8 * mm))

    story.append(
        Paragraph(
            "Company Universe",
            heading_style,
        )
    )

    company_data = [[
        "Company",
        "Sub-Sector",
        "ROE",
        "ROCE",
        "Rev CAGR",
        "PAT CAGR",
        "P/E",
    ]]

    for row in rows:
        company_data.append([
            Paragraph(
                f"{row['company_id']}<br/>"
                f"{row['company_name']}",
                small_style,
            ),
            Paragraph(
                str(row["sub_sector"] or "N/A"),
                small_style,
            ),
            safe_number(row["roe_pct"]),
            safe_number(row["roce_pct"]),
            safe_number(
                row["revenue_cagr_5yr"]
            ),
            safe_number(
                row["pat_cagr_5yr"]
            ),
            safe_number(row["pe_ratio"]),
        ])

    company_table = Table(
        company_data,
        colWidths=[
            38 * mm,
            34 * mm,
            18 * mm,
            18 * mm,
            22 * mm,
            22 * mm,
            18 * mm,
        ],
        repeatRows=1,
    )

    company_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#E5E7EB"),
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.25,
                colors.HexColor("#CCCCCC"),
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                6.5,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#FAFAFA"),
                ],
            ),
            (
                "ALIGN",
                (2, 1),
                (-1, -1),
                "RIGHT",
            ),
        ])
    )

    story.append(company_table)

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Sector Interpretation",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            (
                f"The {sector} sector contains "
                f"{summary['companies']} companies in the "
                "project universe. The statistics in this report "
                "are calculated directly from the project's "
                "validated SQLite dataset. Median-based measures "
                "are used to reduce distortion from extreme "
                "company-level observations."
            ),
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            "Analytical Notes",
            heading_style,
        )
    )

    notes = [
        (
            "ROE and ROCE represent profitability and "
            "capital-efficiency measures."
        ),
        (
            "Revenue CAGR and PAT CAGR represent the "
            "available five-year growth indicators."
        ),
        (
            "CFO margin provides a cash-generation quality "
            "indicator."
        ),
        (
            "P/E and P/B are presented as sector-relative "
            "valuation context rather than investment advice."
        ),
        (
            "Unavailable source values are displayed as N/A "
            "and are excluded from median calculations."
        ),
    ]

    for note in notes:
        story.append(
            Paragraph(
                f"• {note}",
                styles["BodyText"],
            )
        )
        story.append(Spacer(1, 2 * mm))

    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            "Data Source",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            (
                "Source: Nifty 100 Financial Intelligence "
                "Platform database (nifty100.db). "
                "The report uses company master, sector, "
                "financial-ratio and market-cap tables. "
                "Missing source observations are not fabricated."
            ),
            styles["BodyText"],
        )
    )

    document.build(story)

    return output_path



def main():
    """Generate and validate all broad-sector reports."""

    rows = load_sector_data()

    grouped = {}

    for row in rows:
        sector = row["broad_sector"]

        if sector not in grouped:
            grouped[sector] = []

        grouped[sector].append(row)

    generated = []

    # Generate one aggregate comparison report covering all sectors.
    summary_path = generate_all_sectors_summary(grouped)
    generated.append(summary_path)

    print(
        "GENERATED:",
        "All Sectors Summary",
        "| Companies:",
        len(rows),
        "|",
        summary_path,
    )

    # Generate one report for each real broad sector.
    for sector in sorted(grouped):
        path = generate_sector_report(
            sector,
            grouped[sector],
        )

        generated.append(path)

        print(
            "GENERATED:",
            sector,
            "| Companies:",
            len(grouped[sector]),
            "|",
            path,
        )

    valid = [
        path
        for path in generated
        if path.exists()
        and path.stat().st_size > 0
    ]

    print(
        "\n=== SECTOR REPORT QA ==="
    )

    print(
        "TOTAL SECTORS:",
        len(grouped),
    )

    print(
        "TOTAL COMPANIES:",
        len(rows),
    )

    print(
        "SECTOR REPORTS GENERATED:",
        len(generated),
    )

    print(
        "VALID PDF FILES:",
        len(valid),
    )

    print(
        "OUTPUT DIRECTORY:",
        OUTPUT_DIR,
    )

    passed = (
        len(grouped) == 10
        and len(rows) == 92
        and len(generated) == 11
        and len(valid) == 11
    )

    print(
        "SECTOR REPORT STATUS:",
        "PASS" if passed else "FAIL",
    )


if __name__ == "__main__":
    main()























