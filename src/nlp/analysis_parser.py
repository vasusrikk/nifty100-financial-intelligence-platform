"""Day 29 - NLP parser for analysis.xlsx financial text."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ANALYSIS_PATH = (
    PROJECT_ROOT
    / "data"
    / "Raw"
    / "1788501604303-57986a9b-analysis.xlsx"
)

OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_PATH = (
    OUTPUT_DIR
    / "analysis_parsed.csv"
)


# ============================================================
# TEXT PARSER
# ============================================================

def clean_text(value):
    """Return normalized text from an Excel cell."""

    if value is None or pd.isna(value):
        return None

    text = str(value).strip()

    if not text:
        return None

    # Collapse repeated spaces, tabs and line breaks.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def parse_metric_text(value):
    """
    Parse financial text such as:

        10 Years: 21%
        5 Years: 24%
        3 Years: -1%
        TTM: -3%
        1 Year: 16%
        Last Year: 12%

    Returns:
        {
            "period": str | None,
            "value_pct": float | None
        }
    """

    text = clean_text(value)

    if text is None:
        return {
            "period": None,
            "value_pct": None,
        }
        

    pattern = re.compile(
    r"^(.*?)\s*:?\s*"
    r"([-+]?\d+(?:\.\d+)?)\s*%?\s*$",
    flags=re.IGNORECASE,
   ) 

    match = pattern.match(text)

    if match is None:
        return {
            "period": None,
            "value_pct": None,
        }

    period = (
        match.group(1)
        .strip()
    )

    value_pct = float(
        match.group(2)
    )

    return {
        "period": period,
        "value_pct": value_pct,
    }


# ============================================================
# WORKBOOK LOADER
# ============================================================

def load_analysis():
    """
    Load the Analysis worksheet.

    The workbook contains a title row at Excel row 1,
    therefore pandas row index 1 is used as the header.
    """

    if not ANALYSIS_PATH.exists():
        raise FileNotFoundError(
            f"Analysis workbook not found: "
            f"{ANALYSIS_PATH}"
        )

    frame = pd.read_excel(
        ANALYSIS_PATH,
        sheet_name="Analysis",
        header=1,
    )

    frame.columns = [
        str(column).strip()
        for column in frame.columns
    ]

    required_columns = [
        "id",
        "company_id",
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in frame.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required analysis columns: "
            + ", ".join(missing_columns)
        )

    return frame[
        required_columns
    ].copy()


# ============================================================
# PARSE ANALYSIS DATA
# ============================================================

def parse_analysis():
    """Parse all financial-text fields into structured values."""

    frame = load_analysis()

    metric_columns = {
        "compounded_sales_growth":
            "sales_growth",

        "compounded_profit_growth":
            "profit_growth",

        "stock_price_cagr":
            "stock_price_cagr",

        "roe":
            "roe",
    }

    output_rows = []

    for row in frame.itertuples(
        index=False
    ):

        output = {
            "id": row.id,
            "company_id": (
                str(row.company_id).strip()
            ),
        }

        for (
            source_column,
            output_prefix,
        ) in metric_columns.items():

            raw_value = getattr(
                row,
                source_column,
            )

            parsed = parse_metric_text(
                raw_value
            )

            output[
                f"{output_prefix}_raw"
            ] = clean_text(
                raw_value
            )

            output[
                f"{output_prefix}_period"
            ] = parsed[
                "period"
            ]

            output[
                f"{output_prefix}_pct"
            ] = parsed[
                "value_pct"
            ]

        output_rows.append(
            output
        )

    return pd.DataFrame(
        output_rows
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_parsing(frame):
    """Return basic parser validation statistics."""

    metric_prefixes = [
        "sales_growth",
        "profit_growth",
        "stock_price_cagr",
        "roe",
    ]

    statistics = {}

    for prefix in metric_prefixes:

        raw_column = (
            f"{prefix}_raw"
        )

        value_column = (
            f"{prefix}_pct"
        )

        raw_count = int(
            frame[
                raw_column
            ].notna().sum()
        )

        parsed_count = int(
            frame[
                value_column
            ].notna().sum()
        )

        statistics[prefix] = {
            "raw_values":
                raw_count,

            "parsed_values":
                parsed_count,

            "unparsed_values":
                raw_count
                - parsed_count,
        }

    return statistics


# ============================================================
# EXPORT
# ============================================================

def save_parsed_analysis(frame):
    """Save parsed analysis data to CSV."""

    OUTPUT_DIR.mkdir(
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

    parsed = parse_analysis()

    statistics = validate_parsing(
        parsed
    )

    save_parsed_analysis(
        parsed
    )

    print(
        "ANALYSIS PARSER COMPLETE"
    )

    print(
        "ROWS:",
        len(parsed),
    )

    print(
        "COMPANIES:",
        parsed[
            "company_id"
        ].nunique(),
    )

    print(
        "\nPARSER VALIDATION:"
    )

    for (
        metric,
        values,
    ) in statistics.items():

        print(
            metric,
            "| raw:",
            values[
                "raw_values"
            ],
            "| parsed:",
            values[
                "parsed_values"
            ],
            "| unparsed:",
            values[
                "unparsed_values"
            ],
        )

    print(
        "\nOUTPUT:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()