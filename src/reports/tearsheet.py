"""Sprint 5 - Day 33: Two-page Company PDF Tearsheet.

Generates a professional two-page company financial tear sheet.

Page 1:
- Company header
- Six KPI tiles
- Revenue chart
- Net Profit chart
- ROE / ROCE chart

Page 2:
- Balance-sheet composition
- Cash-flow waterfall
- Generated Pros
- Generated Cons
- Capital-allocation badge

The implementation uses ReportLab for the PDF and Matplotlib
for financial charts.
"""

from __future__ import annotations

import io
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "nifty100.db"

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "tearsheets"
)

OUTPUT_DIR = PROJECT_ROOT / "output"

CAPITAL_ALLOCATION_PATH = (
    OUTPUT_DIR
    / "capital_allocation_matrix.csv"
)


# ============================================================
# COLOURS
# ============================================================

NAVY = colors.HexColor("#14213D")
DARK_BLUE = colors.HexColor("#1F4E78")
LIGHT_BLUE = colors.HexColor("#EAF2F8")

GREEN = colors.HexColor("#1B7F3A")
LIGHT_GREEN = colors.HexColor("#EAF7EE")

RED = colors.HexColor("#B3261E")
LIGHT_RED = colors.HexColor("#FCEBEC")

GOLD = colors.HexColor("#D4A017")
LIGHT_GREY = colors.HexColor("#F3F4F6")
MID_GREY = colors.HexColor("#D1D5DB")
DARK_GREY = colors.HexColor("#374151")

WHITE = colors.white
BLACK = colors.black


# ============================================================
# DOCUMENT CONSTANTS
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

LEFT_MARGIN = 12 * mm
RIGHT_MARGIN = 12 * mm
TOP_MARGIN = 10 * mm
BOTTOM_MARGIN = 10 * mm

CONTENT_WIDTH = (
    PAGE_WIDTH
    - LEFT_MARGIN
    - RIGHT_MARGIN
)


# ============================================================
# PARAGRAPH STYLES
# ============================================================

NORMAL_STYLE = ParagraphStyle(
    "NormalWrapped",
    fontName="Helvetica",
    fontSize=7.5,
    leading=9.5,
    textColor=DARK_GREY,
    alignment=TA_LEFT,
    wordWrap="CJK",
)

SMALL_STYLE = ParagraphStyle(
    "SmallWrapped",
    fontName="Helvetica",
    fontSize=6.7,
    leading=8.2,
    textColor=DARK_GREY,
    alignment=TA_LEFT,
    wordWrap="CJK",
)

SECTION_STYLE = ParagraphStyle(
    "Section",
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=12,
    textColor=NAVY,
    spaceAfter=3,
    wordWrap="CJK",
)

KPI_LABEL_STYLE = ParagraphStyle(
    "KPILabel",
    fontName="Helvetica",
    fontSize=6.5,
    leading=7.5,
    textColor=DARK_GREY,
    alignment=TA_CENTER,
    wordWrap="CJK",
)

KPI_VALUE_STYLE = ParagraphStyle(
    "KPIValue",
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=13,
    textColor=NAVY,
    alignment=TA_CENTER,
    wordWrap="CJK",
)

PRO_STYLE = ParagraphStyle(
    "Pro",
    fontName="Helvetica",
    fontSize=6.8,
    leading=8.3,
    textColor=GREEN,
    alignment=TA_LEFT,
    wordWrap="CJK",
)

CON_STYLE = ParagraphStyle(
    "Con",
    fontName="Helvetica",
    fontSize=6.8,
    leading=8.3,
    textColor=RED,
    alignment=TA_LEFT,
    wordWrap="CJK",
)

BADGE_STYLE = ParagraphStyle(
    "Badge",
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=10,
    textColor=NAVY,
    alignment=TA_CENTER,
    wordWrap="CJK",
)


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_number(
    value,
    digits=2,
):
    """Return a formatted number or N/A."""

    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"

        return f"{float(value):,.{digits}f}"

    except (
        TypeError,
        ValueError,
    ):
        return "N/A"


def safe_percent(
    value,
    digits=1,
):
    """Return a formatted percentage."""

    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"

        return (
            f"{float(value):,.{digits}f}%"
        )

    except (
        TypeError,
        ValueError,
    ):
        return "N/A"


def safe_ratio(
    value,
    digits=2,
):
    """Return a formatted ratio."""

    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"

        return (
            f"{float(value):,.{digits}f}x"
        )

    except (
        TypeError,
        ValueError,
    ):
        return "N/A"


def wrapped(
    value,
    style=NORMAL_STYLE,
):
    """Create a word-wrapped ReportLab Paragraph."""

    if value is None:
        value = ""

    return Paragraph(
        str(value),
        style,
    )


def year_sort_value(
    value,
):
    """Extract sortable year component."""

    try:
        return int(
            str(value)[:4]
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0


# ============================================================
# DATABASE HELPERS
# ============================================================

def connect():
    """Open SQLite connection."""

    return sqlite3.connect(
        DB_PATH
    )


def load_company(
    company_id,
):
    """Load company master information."""

    query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            c.book_value,
            c.roce_percentage,
            c.roe_percentage,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category
        FROM companies c
        LEFT JOIN sectors s
            ON s.company_id = c.id
        WHERE c.id = ?
        LIMIT 1
    """

    with connect() as connection:

        frame = pd.read_sql_query(
            query,
            connection,
            params=(company_id,),
        )

    if frame.empty:
        raise ValueError(
            f"Company not found: {company_id}"
        )

    return frame.iloc[0]


def load_profit_loss(
    company_id,
):
    """Load company P&L history."""

    query = """
        SELECT
            company_id,
            year,
            sales,
            operating_profit,
            opm_percentage,
            net_profit,
            eps,
            dividend_payout
        FROM profitandloss
        WHERE company_id = ?
    """

    with connect() as connection:

        frame = pd.read_sql_query(
            query,
            connection,
            params=(company_id,),
        )

    if not frame.empty:

        frame["_sort_year"] = (
            frame["year"]
            .apply(year_sort_value)
        )

        frame = (
            frame
            .sort_values(
                [
                    "_sort_year",
                    "year",
                ]
            )
            .drop(
                columns="_sort_year"
            )
        )

    return frame


def load_balance_sheet(
    company_id,
):
    """Load balance-sheet history."""

    query = """
        SELECT
            company_id,
            year,
            equity_capital,
            reserves,
            borrowings,
            other_liabilities,
            total_liabilities,
            fixed_assets,
            cwip,
            investments,
            other_asset,
            total_assets
        FROM balancesheet
        WHERE company_id = ?
    """

    with connect() as connection:

        frame = pd.read_sql_query(
            query,
            connection,
            params=(company_id,),
        )

    if not frame.empty:

        frame["_sort_year"] = (
            frame["year"]
            .apply(year_sort_value)
        )

        frame = (
            frame
            .sort_values(
                [
                    "_sort_year",
                    "year",
                ]
            )
            .drop(
                columns="_sort_year"
            )
        )

    return frame


def load_cashflow(
    company_id,
):
    """Load cash-flow history."""

    query = """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity,
            net_cash_flow
        FROM cashflow
        WHERE company_id = ?
    """

    with connect() as connection:

        frame = pd.read_sql_query(
            query,
            connection,
            params=(company_id,),
        )

    if not frame.empty:

        frame["_sort_year"] = (
            frame["year"]
            .apply(year_sort_value)
        )

        frame = (
            frame
            .sort_values(
                [
                    "_sort_year",
                    "year",
                ]
            )
            .drop(
                columns="_sort_year"
            )
        )

    return frame


def load_ratios(
    company_id,
):
    """Load financial-ratio history."""

    query = """
        SELECT
            company_id,
            year,
            npm_pct,
            opm_pct,
            roe_pct,
            roce_pct,
            roa_pct,
            de_ratio,
            icr,
            net_debt,
            asset_turnover,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            eps_cagr_5yr,
            cfo_margin_pct,
            cfo_pat_ratio
        FROM financial_ratios
        WHERE company_id = ?
    """

    with connect() as connection:

        frame = pd.read_sql_query(
            query,
            connection,
            params=(company_id,),
        )

    if not frame.empty:

        frame["_sort_year"] = (
            frame["year"]
            .apply(year_sort_value)
        )

        frame = (
            frame
            .sort_values(
                [
                    "_sort_year",
                    "year",
                ]
            )
            .drop(
                columns="_sort_year"
            )
        )

    return frame


def load_pros_cons(
    company_id,
):
    """Load generated Day 30 Pros and Cons."""

    query = """
        SELECT
            company_id,
            signal_type,
            rule_id,
            metric,
            period,
            value_pct,
            message
        FROM generated_pros_cons
        WHERE company_id = ?
        ORDER BY
            signal_type,
            rule_id
    """

    with connect() as connection:

        frame = pd.read_sql_query(
            query,
            connection,
            params=(company_id,),
        )

    return frame


def load_capital_allocation(
    company_id,
):
    """Load Day 32 capital-allocation classification."""

    if not CAPITAL_ALLOCATION_PATH.exists():
        return None

    frame = pd.read_csv(
        CAPITAL_ALLOCATION_PATH
    )

    match = frame[
        frame["company_id"]
        .astype(str)
        .str.strip()
        .str.upper()
        ==
        str(company_id)
        .strip()
        .upper()
    ]

    if match.empty:
        return None

    return match.iloc[0]


# ============================================================
# KPI SELECTION
# ============================================================

def get_latest_row(
    frame,
):
    """Return latest row or None."""

    if frame is None:
        return None

    if frame.empty:
        return None

    return frame.iloc[-1]


def build_kpis(
    profit_loss,
    ratios,
):
    """Build six KPI values for Page 1."""

    latest_pl = get_latest_row(
        profit_loss
    )

    latest_ratio = get_latest_row(
        ratios
    )

    sales = None
    net_profit = None
    eps = None

    if latest_pl is not None:

        sales = latest_pl.get(
            "sales"
        )

        net_profit = latest_pl.get(
            "net_profit"
        )

        eps = latest_pl.get(
            "eps"
        )

    roe = None
    roce = None
    de_ratio = None

    if latest_ratio is not None:

        roe = latest_ratio.get(
            "roe_pct"
        )

        roce = latest_ratio.get(
            "roce_pct"
        )

        de_ratio = latest_ratio.get(
            "de_ratio"
        )

    return [
        (
            "Revenue",
            safe_number(
                sales,
                0,
            ),
        ),
        (
            "Net Profit",
            safe_number(
                net_profit,
                0,
            ),
        ),
        (
            "EPS",
            safe_number(
                eps,
                2,
            ),
        ),
        (
            "ROE",
            safe_percent(
                roe,
                1,
            ),
        ),
        (
            "ROCE",
            safe_percent(
                roce,
                1,
            ),
        ),
        (
            "Debt / Equity",
            safe_ratio(
                de_ratio,
                2,
            ),
        ),
    ]


# ============================================================
# CHART HELPERS
# ============================================================

def figure_to_reportlab_image(
    figure,
    width,
    height,
):
    """Convert Matplotlib figure into ReportLab Image."""

    buffer = io.BytesIO()

    figure.savefig(
        buffer,
        format="png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(
        figure
    )

    buffer.seek(0)

    image = Image(
        buffer,
        width=width,
        height=height,
    )

    image._buffer_reference = buffer

    return image


def empty_chart(
    message,
    width,
    height,
):
    """Generate placeholder when chart data is absent."""

    figure, axis = plt.subplots(
        figsize=(5, 2.5)
    )

    axis.axis(
        "off"
    )

    axis.text(
        0.5,
        0.5,
        message,
        ha="center",
        va="center",
        fontsize=10,
    )

    return figure_to_reportlab_image(
        figure,
        width,
        height,
    )


# ============================================================
# PAGE 1 CHARTS
# ============================================================

def revenue_chart(
    profit_loss,
    width,
    height,
):
    """Create latest ten-observation Revenue bar chart."""

    if profit_loss.empty:
        return empty_chart(
            "Revenue data unavailable",
            width,
            height,
        )

    data = (
        profit_loss
        .tail(10)
        .copy()
    )

    data["sales"] = pd.to_numeric(
        data["sales"],
        errors="coerce",
    )

    figure, axis = plt.subplots(
        figsize=(5.2, 2.5)
    )

    axis.bar(
        data["year"].astype(str),
        data["sales"],
    )

    axis.set_title(
        "Revenue - Latest 10 Years",
        fontsize=9,
        fontweight="bold",
    )

    axis.set_ylabel(
        "Value",
        fontsize=7,
    )

    axis.tick_params(
        axis="x",
        rotation=45,
        labelsize=6,
    )

    axis.tick_params(
        axis="y",
        labelsize=6,
    )

    axis.grid(
        axis="y",
        alpha=0.2,
    )

    figure.tight_layout()

    return figure_to_reportlab_image(
        figure,
        width,
        height,
    )


def profit_chart(
    profit_loss,
    width,
    height,
):
    """Create latest ten-observation Net Profit chart."""

    if profit_loss.empty:
        return empty_chart(
            "Net Profit data unavailable",
            width,
            height,
        )

    data = (
        profit_loss
        .tail(10)
        .copy()
    )

    data["net_profit"] = pd.to_numeric(
        data["net_profit"],
        errors="coerce",
    )

    figure, axis = plt.subplots(
        figsize=(5.2, 2.5)
    )

    axis.bar(
        data["year"].astype(str),
        data["net_profit"],
    )

    axis.set_title(
        "Net Profit - Latest 10 Years",
        fontsize=9,
        fontweight="bold",
    )

    axis.set_ylabel(
        "Value",
        fontsize=7,
    )

    axis.tick_params(
        axis="x",
        rotation=45,
        labelsize=6,
    )

    axis.tick_params(
        axis="y",
        labelsize=6,
    )

    axis.grid(
        axis="y",
        alpha=0.2,
    )

    figure.tight_layout()

    return figure_to_reportlab_image(
        figure,
        width,
        height,
    )


def roe_roce_chart(
    ratios,
    width,
    height,
):
    """Create ROE and ROCE dual-axis line chart."""

    if ratios.empty:
        return empty_chart(
            "ROE / ROCE data unavailable",
            width,
            height,
        )

    data = (
        ratios
        .tail(10)
        .copy()
    )

    data["roe_pct"] = pd.to_numeric(
        data["roe_pct"],
        errors="coerce",
    )

    data["roce_pct"] = pd.to_numeric(
        data["roce_pct"],
        errors="coerce",
    )

    figure, axis_left = plt.subplots(
        figsize=(10, 2.7)
    )

    axis_right = (
        axis_left.twinx()
    )

    x = range(
        len(data)
    )

    axis_left.plot(
        x,
        data["roe_pct"],
        marker="o",
        linewidth=1.6,
        label="ROE",
    )

    axis_right.plot(
        x,
        data["roce_pct"],
        marker="s",
        linewidth=1.6,
        label="ROCE",
    )

    axis_left.set_xticks(
        list(x)
    )

    axis_left.set_xticklabels(
        data["year"].astype(str),
        rotation=45,
        fontsize=6,
    )

    axis_left.set_ylabel(
        "ROE %",
        fontsize=7,
    )

    axis_right.set_ylabel(
        "ROCE %",
        fontsize=7,
    )

    axis_left.tick_params(
        axis="y",
        labelsize=6,
    )

    axis_right.tick_params(
        axis="y",
        labelsize=6,
    )

    axis_left.set_title(
        "ROE and ROCE Trend",
        fontsize=9,
        fontweight="bold",
    )

    lines_1, labels_1 = (
        axis_left
        .get_legend_handles_labels()
    )

    lines_2, labels_2 = (
        axis_right
        .get_legend_handles_labels()
    )

    axis_left.legend(
        lines_1 + lines_2,
        labels_1 + labels_2,
        loc="best",
        fontsize=6,
    )

    axis_left.grid(
        alpha=0.2,
    )

    figure.tight_layout()

    return figure_to_reportlab_image(
        figure,
        width,
        height,
    )


# ============================================================
# PAGE 2 CHARTS
# ============================================================

def balance_sheet_chart(
    balance_sheet,
    width,
    height,
):
    """
    Create stacked balance-sheet composition chart.

    Equity = equity capital + reserves.
    Borrowings and other liabilities are displayed separately.
    """

    if balance_sheet.empty:
        return empty_chart(
            "Balance-sheet data unavailable",
            width,
            height,
        )

    data = (
        balance_sheet
        .tail(10)
        .copy()
    )

    numeric_columns = [
        "equity_capital",
        "reserves",
        "borrowings",
        "other_liabilities",
    ]

    for column in numeric_columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        ).fillna(0)

    data["equity"] = (
        data["equity_capital"]
        + data["reserves"]
    )

    figure, axis = plt.subplots(
        figsize=(10, 2.6)
    )

    x = range(
        len(data)
    )

    axis.bar(
        x,
        data["equity"],
        label="Equity + Reserves",
    )

    axis.bar(
        x,
        data["borrowings"],
        bottom=data["equity"],
        label="Borrowings",
    )

    axis.bar(
        x,
        data["other_liabilities"],
        bottom=(
            data["equity"]
            + data["borrowings"]
        ),
        label="Other Liabilities",
    )

    axis.set_xticks(
        list(x)
    )

    axis.set_xticklabels(
        data["year"].astype(str),
        rotation=45,
        fontsize=6,
    )

    axis.tick_params(
        axis="y",
        labelsize=6,
    )

    axis.set_title(
        "Balance Sheet Composition",
        fontsize=9,
        fontweight="bold",
    )

    axis.legend(
        fontsize=6,
        ncol=3,
        loc="best",
    )

    axis.grid(
        axis="y",
        alpha=0.2,
    )

    figure.tight_layout()

    return figure_to_reportlab_image(
        figure,
        width,
        height,
    )


def cashflow_waterfall(
    cashflow,
    width,
    height,
):
    """
    Create latest-year cash-flow waterfall-style chart.

    Shows:
    CFO
    CFI
    CFF
    Net Cash Flow
    """

    if cashflow.empty:
        return empty_chart(
            "Cash-flow data unavailable",
            width,
            height,
        )

    latest = (
        cashflow.iloc[-1]
    )

    labels = [
        "CFO",
        "CFI",
        "CFF",
        "Net Cash",
    ]

    values = [
        latest[
            "operating_activity"
        ],
        latest[
            "investing_activity"
        ],
        latest[
            "financing_activity"
        ],
        latest[
            "net_cash_flow"
        ],
    ]

    values = [
        0
        if pd.isna(value)
        else float(value)
        for value in values
    ]

    figure, axis = plt.subplots(
        figsize=(10, 2.4)
    )

    axis.bar(
        labels,
        values,
    )

    axis.axhline(
        0,
        linewidth=0.8,
    )

    axis.set_title(
        (
            "Cash Flow - Latest Year "
            f"({latest['year']})"
        ),
        fontsize=9,
        fontweight="bold",
    )

    axis.tick_params(
        axis="x",
        labelsize=7,
    )

    axis.tick_params(
        axis="y",
        labelsize=6,
    )

    axis.grid(
        axis="y",
        alpha=0.2,
    )

    figure.tight_layout()

    return figure_to_reportlab_image(
        figure,
        width,
        height,
    )


# ============================================================
# REPORT COMPONENTS
# ============================================================

def build_header(
    company,
):
    """Create navy company header."""

    company_name = str(
        company["company_name"]
    )

    ticker = str(
        company["company_id"]
    )

    sector = company.get(
        "broad_sector"
    )

    if pd.isna(sector):
        sector = "Sector unavailable"

    left = Paragraph(
        company_name,
        ParagraphStyle(
            "HeaderCompany",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=17,
            textColor=WHITE,
            wordWrap="CJK",
        ),
    )

    right = Paragraph(
        (
            f"<b>{ticker}</b><br/>"
            f"{sector}"
        ),
        ParagraphStyle(
            "HeaderTicker",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=WHITE,
            alignment=TA_CENTER,
            wordWrap="CJK",
        ),
    )

    table = Table(
        [
            [
                left,
                right,
            ]
        ],
        colWidths=[
            CONTENT_WIDTH * 0.72,
            CONTENT_WIDTH * 0.28,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    NAVY,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    return table


def build_kpi_tiles(
    kpis,
):
    """Create six KPI tiles in two rows of three."""

    cells = []

    for label, value in kpis:

        content = [
            [
                Paragraph(
                    label,
                    KPI_LABEL_STYLE,
                )
            ],
            [
                Paragraph(
                    value,
                    KPI_VALUE_STYLE,
                )
            ],
        ]

        tile = Table(
            content,
            colWidths=[
                CONTENT_WIDTH / 3
                - 6
            ],
        )

        tile.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        LIGHT_BLUE,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        MID_GREY,
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
                        4,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )

        cells.append(
            tile
        )

    rows = [
        cells[0:3],
        cells[3:6],
    ]

    table = Table(
        rows,
        colWidths=[
            CONTENT_WIDTH / 3
        ] * 3,
        hAlign="CENTER",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
            ]
        )
    )

    return table



def build_pros_cons_table(
    pros_cons,
):
    """Build overflow-safe Pros and Cons section."""

    # Always keep pros and cons as DataFrames.
    if (
        pros_cons is None
        or pros_cons.empty
    ):

        pros = pd.DataFrame(
            columns=[
                "message"
            ]
        )

        cons = pd.DataFrame(
            columns=[
                "message"
            ]
        )

    else:

        signal_type = (
            pros_cons[
                "signal_type"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )

        pros = (
            pros_cons[
                signal_type == "PRO"
            ]
            .head(4)
            .copy()
        )

        cons = (
            pros_cons[
                signal_type == "CON"
            ]
            .head(4)
            .copy()
        )

    # ========================================================
    # PROS
    # ========================================================

    pro_items = []

    for row in pros.itertuples(
        index=False
    ):

        message = getattr(
            row,
            "message",
            None,
        )

        if (
            message is None
            or pd.isna(message)
        ):
            continue

        pro_items.append(
            Paragraph(
                "&#8226; "
                + str(message),
                PRO_STYLE,
            )
        )

    if not pro_items:

        pro_items.append(
            Paragraph(
                "No generated pro signal available.",
                SMALL_STYLE,
            )
        )

    # ========================================================
    # CONS
    # ========================================================

    con_items = []

    for row in cons.itertuples(
        index=False
    ):

        message = getattr(
            row,
            "message",
            None,
        )

        if (
            message is None
            or pd.isna(message)
        ):
            continue

        con_items.append(
            Paragraph(
                "&#8226; "
                + str(message),
                CON_STYLE,
            )
        )

    if not con_items:

        con_items.append(
            Paragraph(
                "No generated con signal available.",
                SMALL_STYLE,
            )
        )

    # ========================================================
    # PRO TABLE
    # ========================================================

    pro_content = [
        [
            Paragraph(
                "PROS",
                ParagraphStyle(
                    "ProsHeading",
                    parent=SECTION_STYLE,
                    textColor=GREEN,
                ),
            )
        ]
    ]

    for item in pro_items:

        pro_content.append(
            [
                item
            ]
        )

    pro_table = Table(
        pro_content,
        colWidths=[
            CONTENT_WIDTH / 2
            - 6
        ],
    )

    pro_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_GREEN,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    GREEN,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    # ========================================================
    # CON TABLE
    # ========================================================

    con_content = [
        [
            Paragraph(
                "CONS",
                ParagraphStyle(
                    "ConsHeading",
                    parent=SECTION_STYLE,
                    textColor=RED,
                ),
            )
        ]
    ]

    for item in con_items:

        con_content.append(
            [
                item
            ]
        )

    con_table = Table(
        con_content,
        colWidths=[
            CONTENT_WIDTH / 2
            - 6
        ],
    )

    con_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_RED,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    RED,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    # ========================================================
    # COMBINED PRO / CON TABLE
    # ========================================================

    table = Table(
        [
            [
                pro_table,
                con_table,
            ]
        ],
        colWidths=[
            CONTENT_WIDTH / 2,
            CONTENT_WIDTH / 2,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
            ]
        )
    )

    return table






def build_capital_badge(
    allocation,
):
    """Create capital-allocation badge."""

    if allocation is None:

        allocation_class = (
            "CAPITAL ALLOCATION UNAVAILABLE"
        )

        explanation = (
            "Day 32 capital-allocation result "
            "was not found."
        )

    else:

        allocation_class = str(
            allocation.get(
                "allocation_class",
                "UNAVAILABLE",
            )
        )

        explanation = str(
            allocation.get(
                "allocation_explanation",
                "",
            )
        )

    badge = Table(
        [
            [
                Paragraph(
                    (
                        "<b>CAPITAL ALLOCATION</b><br/>"
                        f"{allocation_class}"
                    ),
                    BADGE_STYLE,
                )
            ],
            [
                Paragraph(
                    explanation,
                    SMALL_STYLE,
                )
            ],
        ],
        colWidths=[
            CONTENT_WIDTH
        ],
    )

    badge.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#FFF4CC"
                    ),
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, 1),
                    colors.HexColor(
                        "#FFFBEB"
                    ),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    GOLD,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return badge


# ============================================================
# PAGE FOOTER
# ============================================================

def draw_footer(
    canvas,
    document,
):
    """Draw page number and project footer."""

    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        6.5,
    )

    canvas.setFillColor(
        DARK_GREY
    )

    canvas.drawString(
        LEFT_MARGIN,
        5 * mm,
        (
            "NIFTY100 Financial Intelligence Platform "
            "- Sprint 5"
        ),
    )

    canvas.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        5 * mm,
        f"Page {document.page}",
    )

    canvas.restoreState()


# ============================================================
# TEARSHEET GENERATOR
# ============================================================

def generate_tearsheet(
    company_id,
    output_path=None,
):
    """
    Generate one two-page company PDF tear sheet.

    Returns the generated PDF path.
    """

    company_id = (
        str(company_id)
        .strip()
        .upper()
    )

    company = load_company(
        company_id
    )

    profit_loss = load_profit_loss(
        company_id
    )

    balance_sheet = load_balance_sheet(
        company_id
    )

    cashflow = load_cashflow(
        company_id
    )

    ratios = load_ratios(
        company_id
    )

    pros_cons = load_pros_cons(
        company_id
    )

    allocation = load_capital_allocation(
        company_id
    )

    if output_path is None:

        REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            REPORT_DIR
            / f"{company_id}_tearsheet.pdf"
        )

    else:

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=RIGHT_MARGIN,
        leftMargin=LEFT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title=(
            f"{company_id} Financial Tearsheet"
        ),
        author=(
            "NIFTY100 Financial "
            "Intelligence Platform"
        ),
    )

    story = []

    # ========================================================
    # PAGE 1
    # ========================================================

    story.append(
        build_header(
            company
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm,
        )
    )

    kpis = build_kpis(
        profit_loss,
        ratios,
    )

    story.append(
        build_kpi_tiles(
            kpis
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm,
        )
    )

    story.append(
        Paragraph(
            "Growth & Profitability",
            SECTION_STYLE,
        )
    )

    revenue = revenue_chart(
        profit_loss,
        CONTENT_WIDTH / 2 - 4,
        48 * mm,
    )

    profit = profit_chart(
        profit_loss,
        CONTENT_WIDTH / 2 - 4,
        48 * mm,
    )

    charts = Table(
        [
            [
                revenue,
                profit,
            ]
        ],
        colWidths=[
            CONTENT_WIDTH / 2,
            CONTENT_WIDTH / 2,
        ],
    )

    charts.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    1,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    1,
                ),
            ]
        )
    )

    story.append(
        charts
    )

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    story.append(
        roe_roce_chart(
            ratios,
            CONTENT_WIDTH,
            51 * mm,
        )
    )

    # ========================================================
    # PAGE 2
    # ========================================================

    story.append(
        PageBreak()
    )

    story.append(
        build_header(
            company
        )
    )

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    story.append(
        Paragraph(
            "Balance Sheet Composition",
            SECTION_STYLE,
        )
    )

    story.append(
        balance_sheet_chart(
            balance_sheet,
            CONTENT_WIDTH,
            45 * mm,
        )
    )

    story.append(
        Spacer(
            1,
            2 * mm,
        )
    )

    story.append(
        Paragraph(
            "Cash Flow",
            SECTION_STYLE,
        )
    )

    story.append(
        cashflow_waterfall(
            cashflow,
            CONTENT_WIDTH,
            39 * mm,
        )
    )

    story.append(
        Spacer(
            1,
            2 * mm,
        )
    )

    story.append(
        build_pros_cons_table(
            pros_cons
        )
    )

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    story.append(
        build_capital_badge(
            allocation
        )
    )

    document.build(
        story,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer,
    )

    return output_path


# ============================================================
# DAY 33 TEST COMPANIES
# ============================================================

TEST_COMPANIES = [
    "TCS",
    "HDFCBANK",
    "RELIANCE",
    "SUNPHARMA",
    "TATASTEEL",
]


def test_day33_tearsheets():
    """
    Generate Day 33 tear sheets for five companies from
    different sectors.
    """

    print(
        "DAY 33 PDF TEARSHEET TEST"
    )

    print(
        "=" * 50
    )

    generated = []
    failed = []

    for company_id in TEST_COMPANIES:

        try:

            output_path = (
                generate_tearsheet(
                    company_id
                )
            )

            generated.append(
                str(output_path)
            )

            print(
                "PASS:",
                company_id,
                "->",
                output_path,
            )

        except Exception as error:

            failed.append(
                (
                    company_id,
                    str(error),
                )
            )

            print(
                "FAIL:",
                company_id,
                "->",
                error,
            )

    print(
        "\nGENERATED:",
        len(generated),
    )

    print(
        "FAILED:",
        len(failed),
    )

    print(
        "\nREPORT DIRECTORY:",
        REPORT_DIR,
    )

    if failed:

        print(
            "\nFAILED COMPANIES:"
        )

        for (
            company_id,
            error,
        ) in failed:

            print(
                company_id,
                ":",
                error,
            )

    return (
        generated,
        failed,
    )


# ============================================================
# MAIN
# ============================================================

def main():
    """Execute Sprint 5 Day 33 test generation."""

    generated, failed = (
        test_day33_tearsheets()
    )

    if failed:

        print(
            "\nDAY 33 STATUS: "
            "REQUIRES FIXES"
        )

    else:

        print(
            "\nDAY 33 STATUS: "
            "5 TEST TEARSHEETS GENERATED"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()