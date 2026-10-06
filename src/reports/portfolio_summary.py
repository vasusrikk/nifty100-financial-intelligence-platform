"""Generate the Sprint 6 portfolio-level analytical summary PDF."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
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

INPUT_PATH = (
    PROJECT_ROOT
    / "output"
    / "portfolio_stats.csv"
)
OUTPUT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "portfolio"
    / "portfolio_summary.pdf"
)

KPI_LABELS = {
    "npm_pct": "Net Profit Margin (%)",
    "opm_pct": "Operating Profit Margin (%)",
    "roe_pct": "Return on Equity (%)",
    "roce_pct": "Return on Capital Employed (%)",
    "roa_pct": "Return on Assets (%)",
    "de_ratio": "Debt-to-Equity",
    "icr": "Interest Coverage Ratio",
    "asset_turnover": "Asset Turnover",
    "revenue_cagr_5yr": "Revenue CAGR - 5Y (%)",
    "cfo_margin_pct": "CFO Margin (%)",
}


def fmt(value):
    """Format numeric values for the PDF."""
    if pd.isna(value):
        return "N/A"

    return f"{float(value):.2f}"


def build_pdf():
    """Build portfolio_summary.pdf from Day 37 portfolio statistics."""

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Portfolio statistics not found: {INPUT_PATH}"
        )

    data = pd.read_csv(INPUT_PATH)

    required_columns = {
        "kpi",
        "count",
        "p10",
        "p25",
        "p50",
        "p75",
        "p90",
        "mean",
        "std",
    }

    missing_columns = (
        required_columns - set(data.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing portfolio statistics columns: "
            + ", ".join(sorted(missing_columns))
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="NIFTY 100 Portfolio Summary",
        author="NIFTY 100 Financial Intelligence Platform",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PortfolioTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "PortfolioSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#555555"),
        spaceAfter=15,
    )

    heading_style = ParagraphStyle(
        "PortfolioHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=17,
        spaceBefore=8,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "PortfolioBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        spaceAfter=6,
    )

    story = []

    story.append(
        Paragraph(
            "NIFTY 100 Financial Intelligence Platform",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Portfolio Statistics & Distribution Summary",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            "Portfolio Overview",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            (
                "This report summarizes the portfolio-level "
                "distribution of ten financial KPIs generated "
                "by the Sprint 6 Day 37 analytics pipeline. "
                "The statistics are derived from "
                "output/portfolio_stats.csv."
            ),
            body_style,
        )
    )

    story.append(
        Paragraph(
            (
                "Percentile statistics are emphasized because "
                "financial datasets may contain extreme "
                "company-level observations. The median (P50) "
                "therefore provides a robust representation of "
                "the central company in the observed universe."
            ),
            body_style,
        )
    )

    story.append(Spacer(1, 5 * mm))

    table_data = [[
        "KPI",
        "Count",
        "P10",
        "P25",
        "Median\n(P50)",
        "P75",
        "P90",
        "Mean",
        "Std Dev",
    ]]

    for _, row in data.iterrows():

        label = KPI_LABELS.get(
            row["kpi"],
            row["kpi"],
        )

        table_data.append([
            label,
            str(int(row["count"])),
            fmt(row["p10"]),
            fmt(row["p25"]),
            fmt(row["p50"]),
            fmt(row["p75"]),
            fmt(row["p90"]),
            fmt(row["mean"]),
            fmt(row["std"]),
        ])

    table = Table(
        table_data,
        colWidths=[
            55 * mm,
            17 * mm,
            21 * mm,
            21 * mm,
            23 * mm,
            21 * mm,
            21 * mm,
            23 * mm,
            23 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(
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
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F8F9FA"),
                ],
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7.5,
            ),
            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "RIGHT",
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
        ])
    )

    story.append(table)

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Portfolio Distribution Interpretation",
            heading_style,
        )
    )

    for _, row in data.iterrows():

        label = KPI_LABELS.get(
            row["kpi"],
            row["kpi"],
        )

        text = (
            f"<b>{label}</b> — "
            f"Coverage: {int(row['count'])} observations; "
            f"P10: {fmt(row['p10'])}; "
            f"P25: {fmt(row['p25'])}; "
            f"Median: {fmt(row['p50'])}; "
            f"P75: {fmt(row['p75'])}; "
            f"P90: {fmt(row['p90'])}."
        )

        story.append(
            Paragraph(
                text,
                body_style,
            )
        )

    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            "Methodology Notes",
            heading_style,
        )
    )

    notes = [
        (
            "P10, P25, P50, P75 and P90 describe the "
            "cross-sectional distribution of each KPI."
        ),
        (
            "P50 is the median and is less sensitive to "
            "extreme observations than the arithmetic mean."
        ),
        (
            "Count represents the number of available "
            "company observations used for each KPI."
        ),
        (
            "Different KPI counts reflect unavailable source "
            "observations; missing financial values are not "
            "fabricated."
        ),
        (
            "Mean and standard deviation are retained for "
            "statistical completeness, but should be interpreted "
            "carefully when distributions contain outliers."
        ),
        (
            "This document is an analytical summary of the "
            "project dataset and does not constitute investment "
            "advice."
        ),
    ]

    for note in notes:
        story.append(
            Paragraph(
                f"• {note}",
                body_style,
            )
        )

    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            "Source",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            (
                "Sprint 6 Day 37 portfolio statistics generated "
                "by src/analytics/cluster_profiling.py and stored "
                "in output/portfolio_stats.csv."
            ),
            body_style,
        )
    )

    document.build(story)

    return OUTPUT_PATH


def main():
    """Generate and validate the portfolio summary."""

    output = build_pdf()

    data = pd.read_csv(INPUT_PATH)

    valid = (
        output.exists()
        and output.stat().st_size > 0
        and len(data) == 10
    )

    print(
        "\n=== PORTFOLIO SUMMARY PDF QA ==="
    )
    print(
        "PORTFOLIO KPI ROWS:",
        len(data),
    )
    print(
        "SOURCE:",
        INPUT_PATH,
    )
    print(
        "PDF:",
        output,
    )
    print(
        "PDF EXISTS:",
        output.exists(),
    )

    if output.exists():
        print(
            "PDF SIZE:",
            output.stat().st_size,
            "bytes",
        )

    print(
        "PORTFOLIO SUMMARY STATUS:",
        "PASS" if valid else "FAIL",
    )


if __name__ == "__main__":
    main()