"""Sprint 5 - Day 29: NLP Analysis Text Parser."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src.analytics.cagr import build_cagr_engine


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

PARSED_OUTPUT = OUTPUT_DIR / "analysis_parsed.csv"
FAILURE_OUTPUT = OUTPUT_DIR / "parse_failures.csv"
VALIDATION_OUTPUT = OUTPUT_DIR / "analysis_cagr_validation.csv"


# ============================================================
# CONFIGURATION
# ============================================================

METRIC_COLUMNS = {
    "compounded_sales_growth": "revenue_cagr",
    "compounded_profit_growth": "pat_cagr",
    "stock_price_cagr": "stock_price_cagr",
    "roe": "roe",
}

CAGR_ENGINE_COLUMNS = {
    "revenue_cagr": "revenue",
    "pat_cagr": "pat",
}

DIVERGENCE_THRESHOLD = 5.0


# ============================================================
# TEXT HELPERS
# ============================================================

def clean_text(value):
    """Normalize an Excel text value."""

    if value is None or pd.isna(value):
        return None

    text = str(value).strip()

    if not text:
        return None

    return re.sub(r"\s+", " ", text)


def parse_period(period_text):
    """Convert period text into number of years."""

    if period_text is None:
        return None

    normalized = str(period_text).strip().lower()

    if normalized == "ttm":
        return 0

    if normalized == "last year":
        return 1

    match = re.search(
        r"(\d+)\s*years?",
        normalized,
    )

    if match:
        return int(match.group(1))

    return None


def parse_metric_text(value):
    """Parse financial-analysis text into period and percentage."""

    text = clean_text(value)

    if text is None:
        return None

    pattern = re.compile(
        r"^(.*?)\s*:?\s*"
        r"([-+]?\d+(?:\.\d+)?)\s*%\s*$",
        flags=re.IGNORECASE,
    )

    match = pattern.match(text)

    if match is None:
        return None

    period_text = match.group(1).strip()
    period_years = parse_period(period_text)

    if period_years is None:
        return None

    return {
        "period_text": period_text,
        "period_years": period_years,
        "value_pct": float(match.group(2)),
    }


# ============================================================
# LOAD ANALYSIS WORKBOOK
# ============================================================

def load_analysis():
    """Load the Analysis worksheet."""

    if not ANALYSIS_PATH.exists():
        raise FileNotFoundError(
            f"Analysis workbook not found: {ANALYSIS_PATH}"
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
        *METRIC_COLUMNS.keys(),
    ]

    missing = [
        column
        for column in required_columns
        if column not in frame.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    return frame[required_columns].copy()


# ============================================================
# PARSER
# ============================================================

def parse_analysis():
    """Parse Analysis workbook into normalized rows."""

    source = load_analysis()

    parsed_rows = []
    failure_rows = []

    for row in source.itertuples(index=False):

        company_id = str(row.company_id).strip()

        for source_column, metric_type in METRIC_COLUMNS.items():

            raw_value = getattr(
                row,
                source_column,
            )

            cleaned = clean_text(raw_value)

            if cleaned is None:
                continue

            parsed = parse_metric_text(cleaned)

            if parsed is None:

                failure_rows.append(
                    {
                        "source_id": row.id,
                        "company_id": company_id,
                        "metric_type": metric_type,
                        "raw_text": cleaned,
                        "failure_reason":
                            "REGEX_OR_PERIOD_UNMATCHED",
                    }
                )

                continue

            parsed_rows.append(
                {
                    "company_id": company_id,
                    "metric_type": metric_type,
                    "period_years":
                        parsed["period_years"],
                    "value_pct":
                        parsed["value_pct"],
                }
            )

    parsed_frame = pd.DataFrame(
        parsed_rows,
        columns=[
            "company_id",
            "metric_type",
            "period_years",
            "value_pct",
        ],
    )

    failures_frame = pd.DataFrame(
        failure_rows,
        columns=[
            "source_id",
            "company_id",
            "metric_type",
            "raw_text",
            "failure_reason",
        ],
    )

    return parsed_frame, failures_frame


# ============================================================
# CAGR CROSS-VALIDATION
# ============================================================

def build_cagr_validation(parsed_frame):
    """
    Compare parsed Revenue/PAT CAGR against the existing
    Sprint 2 CAGR engine.

    Divergence above 5 percentage points is flagged for
    manual review.
    """

    engine = build_cagr_engine()

    if engine.empty:
        return pd.DataFrame()

    engine = engine.copy()

    engine["_year_sort"] = pd.to_numeric(
        engine["year"]
        .astype(str)
        .str[:4],
        errors="coerce",
    )

    latest_engine = (
        engine
        .sort_values(
            [
                "company_id",
                "_year_sort",
                "year",
            ]
        )
        .groupby(
            "company_id",
            as_index=False,
        )
        .tail(1)
    )

    engine_lookup = {
        str(row["company_id"]): row
        for _, row in latest_engine.iterrows()
    }

    comparable = parsed_frame[
        parsed_frame["metric_type"].isin(
            CAGR_ENGINE_COLUMNS.keys()
        )
        &
        parsed_frame["period_years"].isin(
            [3, 5, 10]
        )
    ]

    validation_rows = []

    for _, row in comparable.iterrows():

        company_id = str(row["company_id"])
        metric_type = row["metric_type"]
        period_years = int(row["period_years"])
        parsed_value = row["value_pct"]

        engine_metric = CAGR_ENGINE_COLUMNS[
            metric_type
        ]

        engine_column = (
            f"{engine_metric}_cagr_{period_years}yr"
        )

        engine_flag_column = (
            f"{engine_column}_flag"
        )

        engine_row = engine_lookup.get(
            company_id
        )

        engine_year = None
        engine_value = None
        engine_flag = "ENGINE_ROW_MISSING"

        if engine_row is not None:

            engine_year = engine_row.get("year")

            if engine_column in engine_row.index:
                engine_value = engine_row.get(
                    engine_column
                )

            if engine_flag_column in engine_row.index:
                engine_flag = engine_row.get(
                    engine_flag_column
                )

        if pd.isna(engine_value):
            engine_value = None

        if (
            engine_value is not None
            and pd.notna(parsed_value)
        ):

            divergence = abs(
                float(parsed_value)
                - float(engine_value)
            )

            manual_review = (
                divergence
                > DIVERGENCE_THRESHOLD
            )

            status = (
                "MANUAL_REVIEW"
                if manual_review
                else "PASS"
            )

        else:

            divergence = None
            manual_review = False
            status = "NOT_COMPARABLE"

        validation_rows.append(
            {
                "company_id": company_id,
                "metric_type": metric_type,
                "period_years": period_years,
                "parsed_value_pct": parsed_value,
                "engine_year": engine_year,
                "engine_value_pct": engine_value,
                "engine_flag": engine_flag,
                "divergence_pct_points": divergence,
                "manual_review": manual_review,
                "validation_status": status,
            }
        )

    return pd.DataFrame(validation_rows)


# ============================================================
# SAVE OUTPUTS
# ============================================================

def save_outputs(
    parsed_frame,
    failures_frame,
    validation_frame,
):
    """Save all Day 29 outputs."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    parsed_frame.to_csv(
        PARSED_OUTPUT,
        index=False,
    )

    failures_frame.to_csv(
        FAILURE_OUTPUT,
        index=False,
    )

    validation_frame.to_csv(
        VALIDATION_OUTPUT,
        index=False,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    parsed, failures = parse_analysis()

    validation = build_cagr_validation(
        parsed
    )

    save_outputs(
        parsed,
        failures,
        validation,
    )

    print("DAY 29 ANALYSIS PARSER COMPLETE")

    print(
        "PARSED ROWS:",
        len(parsed),
    )

    print(
        "COMPANIES:",
        parsed["company_id"].nunique(),
    )

    print(
        "PARSE FAILURES:",
        len(failures),
    )

    print(
        "CAGR VALIDATIONS:",
        len(validation),
    )

    if not validation.empty:

        pass_count = int(
            (
                validation["validation_status"]
                == "PASS"
            ).sum()
        )

        review_count = int(
            (
                validation["validation_status"]
                == "MANUAL_REVIEW"
            ).sum()
        )

        not_comparable = int(
            (
                validation["validation_status"]
                == "NOT_COMPARABLE"
            ).sum()
        )

        print(
            "VALIDATION PASS:",
            pass_count,
        )

        print(
            "MANUAL REVIEW:",
            review_count,
        )

        print(
            "NOT COMPARABLE:",
            not_comparable,
        )

    print(
        "PARSED OUTPUT:",
        PARSED_OUTPUT,
    )

    print(
        "FAILURES OUTPUT:",
        FAILURE_OUTPUT,
    )

    print(
        "VALIDATION OUTPUT:",
        VALIDATION_OUTPUT,
    )


if __name__ == "__main__":
    main()