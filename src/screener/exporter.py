"""Sprint 3 - Day 20: Screener Export Engine."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from src.screener.custom_screener import run_custom_screener
from src.screener.scoring import rank_companies


# ============================================================
# EXPORT CONFIGURATION
# ============================================================

EXPORT_COLUMNS = [
    "rank",
    "company_id",
    "company_name",
    "year",
    "broad_sector",
    "sub_sector",
    "composite_score",
    "score_coverage_pct",
    "roe_pct",
    "roce_pct",
    "npm_pct",
    "opm_pct",
    "de_ratio",
    "icr",
    "asset_turnover",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "cfo_margin_pct",
    "pe_ratio",
    "pb_ratio",
    "dividend_yield_pct",
    "market_cap_crore",
]


SUPPORTED_EXPORT_FORMATS = {
    "csv",
    "json",
}


# ============================================================
# PATH HELPERS
# ============================================================

def ensure_export_directory(
    directory="reports",
):
    """
    Create the export directory when it does not exist.
    """

    path = Path(directory)

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def validate_export_format(
    export_format,
):
    """
    Validate and normalize an export format.
    """

    export_format = str(
        export_format
    ).strip().lower()

    if (
        export_format
        not in SUPPORTED_EXPORT_FORMATS
    ):
        raise ValueError(
            "Unsupported export format: "
            f"{export_format}"
        )

    return export_format


# ============================================================
# ROW PREPARATION
# ============================================================

def prepare_export_row(row):
    """
    Keep only stable public screener fields.

    Internal structures such as metric_scores are deliberately
    excluded from flat exports.
    """

    return {
        column: row.get(column)
        for column in EXPORT_COLUMNS
    }


def prepare_export_rows(rows):
    """
    Prepare all rows for export.
    """

    if rows is None:
        raise ValueError(
            "Rows are required for export."
        )

    return [
        prepare_export_row(row)
        for row in rows
    ]


# ============================================================
# CSV EXPORT
# ============================================================

def export_csv(
    rows,
    file_path,
):
    """
    Export screener rows to CSV.
    """

    prepared = prepare_export_rows(
        rows
    )

    file_path = Path(file_path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with file_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=EXPORT_COLUMNS,
        )

        writer.writeheader()

        writer.writerows(
            prepared
        )

    return file_path


# ============================================================
# JSON EXPORT
# ============================================================

def export_json(
    rows,
    file_path,
):
    """
    Export screener rows to readable JSON.
    """

    prepared = prepare_export_rows(
        rows
    )

    file_path = Path(file_path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            prepared,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return file_path


# ============================================================
# GENERAL EXPORT
# ============================================================

def export_results(
    rows,
    filename,
    export_format="csv",
    directory="reports",
):
    """
    Export screener results using the requested format.
    """

    export_format = (
        validate_export_format(
            export_format
        )
    )

    export_directory = (
        ensure_export_directory(
            directory
        )
    )

    filename = str(
        filename
    ).strip()

    if not filename:
        raise ValueError(
            "Export filename is required."
        )

    file_path = (
        export_directory
        / f"{filename}.{export_format}"
    )

    if export_format == "csv":
        return export_csv(
            rows,
            file_path,
        )

    return export_json(
        rows,
        file_path,
    )


# ============================================================
# RANKED UNIVERSE EXPORT
# ============================================================

def export_ranked_universe(
    filename="nifty100_ranked",
    export_format="csv",
    directory="reports",
):
    """
    Rank the complete screener universe and export it.
    """

    rows = rank_companies()

    return export_results(
        rows,
        filename,
        export_format,
        directory,
    )


# ============================================================
# CUSTOM SCREEN EXPORT
# ============================================================

def export_custom_screen(
    filters,
    filename="custom_screen",
    export_format="csv",
    directory="reports",
):
    """
    Run a custom screen and export its ranked matches.
    """

    output = run_custom_screener(
        filters,
        rank_results=True,
    )

    return export_results(
        output["results"],
        filename,
        export_format,
        directory,
    )


# ============================================================
# DAY 20 QA
# ============================================================

def main():

    filters = [
        {
            "metric": "roe_pct",
            "operator": ">",
            "value": 15,
        },
        {
            "metric": "de_ratio",
            "operator": "<",
            "value": 1,
        },
        {
            "metric": "revenue_cagr_5yr",
            "operator": ">",
            "value": 10,
        },
    ]

    output = run_custom_screener(
        filters
    )

    export_directory = (
        ensure_export_directory(
            "reports"
        )
    )

    csv_path = export_results(
        output["results"],
        "day20_custom_screen",
        "csv",
        export_directory,
    )

    json_path = export_results(
        output["results"],
        "day20_custom_screen",
        "json",
        export_directory,
    )

    print(
        "\n=== SPRINT 3 - DAY 20 "
        "EXPORT ENGINE QA ==="
    )

    print(
        "Rows exported:",
        len(output["results"]),
    )

    print(
        "Export columns:",
        len(EXPORT_COLUMNS),
    )

    print(
        "CSV:",
        csv_path,
    )

    print(
        "JSON:",
        json_path,
    )

    print(
        "CSV exists:",
        csv_path.exists(),
    )

    print(
        "JSON exists:",
        json_path.exists(),
    )

    print(
        "CSV size:",
        csv_path.stat().st_size,
        "bytes",
    )

    print(
        "JSON size:",
        json_path.stat().st_size,
        "bytes",
    )


if __name__ == "__main__":
    main()