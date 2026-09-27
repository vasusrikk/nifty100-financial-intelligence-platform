import csv
import json

import pytest

from src.screener.exporter import (
    EXPORT_COLUMNS,
    SUPPORTED_EXPORT_FORMATS,
    ensure_export_directory,
    export_csv,
    export_custom_screen,
    export_json,
    export_results,
    prepare_export_row,
    prepare_export_rows,
    validate_export_format,
)
from src.screener.scoring import rank_companies


# ============================================================
# CONFIGURATION
# ============================================================

def test_export_column_count():
    assert len(EXPORT_COLUMNS) == 23


def test_supported_formats():
    assert SUPPORTED_EXPORT_FORMATS == {
        "csv",
        "json",
    }


# ============================================================
# FORMAT VALIDATION
# ============================================================

def test_csv_format():
    assert validate_export_format(
        "csv"
    ) == "csv"


def test_json_format():
    assert validate_export_format(
        "JSON"
    ) == "json"


def test_format_whitespace():
    assert validate_export_format(
        " CSV "
    ) == "csv"


def test_invalid_format():
    with pytest.raises(ValueError):
        validate_export_format(
            "xlsx"
        )


# ============================================================
# ROW PREPARATION
# ============================================================

def test_prepare_export_row():
    ranked = rank_companies()

    row = prepare_export_row(
        ranked[0]
    )

    assert set(
        row.keys()
    ) == set(
        EXPORT_COLUMNS
    )


def test_internal_metric_scores_excluded():
    ranked = rank_companies()

    row = prepare_export_row(
        ranked[0]
    )

    assert "metric_scores" not in row


def test_prepare_rows():
    ranked = rank_companies()

    prepared = prepare_export_rows(
        ranked[:5]
    )

    assert len(prepared) == 5


def test_none_rows_rejected():
    with pytest.raises(ValueError):
        prepare_export_rows(None)


# ============================================================
# DIRECTORY HANDLING
# ============================================================

def test_export_directory_created(
    tmp_path,
):
    directory = (
        tmp_path
        / "exports"
    )

    result = ensure_export_directory(
        directory
    )

    assert result.exists()
    assert result.is_dir()


# ============================================================
# CSV EXPORT
# ============================================================

def test_csv_export(tmp_path):
    rows = rank_companies()[:5]

    path = export_csv(
        rows,
        tmp_path / "test.csv",
    )

    assert path.exists()
    assert path.stat().st_size > 0


def test_csv_row_count(tmp_path):
    rows = rank_companies()[:5]

    path = export_csv(
        rows,
        tmp_path / "test.csv",
    )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = list(
            csv.DictReader(file)
        )

    assert len(reader) == 5


def test_csv_headers(tmp_path):
    rows = rank_companies()[:2]

    path = export_csv(
        rows,
        tmp_path / "test.csv",
    )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        assert (
            reader.fieldnames
            == EXPORT_COLUMNS
        )


# ============================================================
# JSON EXPORT
# ============================================================

def test_json_export(tmp_path):
    rows = rank_companies()[:5]

    path = export_json(
        rows,
        tmp_path / "test.json",
    )

    assert path.exists()
    assert path.stat().st_size > 0


def test_json_valid(tmp_path):
    rows = rank_companies()[:5]

    path = export_json(
        rows,
        tmp_path / "test.json",
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    assert isinstance(data, list)
    assert len(data) == 5


def test_json_columns(tmp_path):
    rows = rank_companies()[:1]

    path = export_json(
        rows,
        tmp_path / "test.json",
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    assert set(
        data[0].keys()
    ) == set(
        EXPORT_COLUMNS
    )


# ============================================================
# GENERAL EXPORT
# ============================================================

def test_general_csv_export(tmp_path):
    rows = rank_companies()[:3]

    path = export_results(
        rows,
        "companies",
        "csv",
        tmp_path,
    )

    assert path.name == (
        "companies.csv"
    )

    assert path.exists()


def test_general_json_export(tmp_path):
    rows = rank_companies()[:3]

    path = export_results(
        rows,
        "companies",
        "json",
        tmp_path,
    )

    assert path.name == (
        "companies.json"
    )

    assert path.exists()


def test_empty_filename_rejected(
    tmp_path,
):
    rows = rank_companies()[:2]

    with pytest.raises(ValueError):
        export_results(
            rows,
            "",
            "csv",
            tmp_path,
        )


def test_invalid_general_format(
    tmp_path,
):
    rows = rank_companies()[:2]

    with pytest.raises(ValueError):
        export_results(
            rows,
            "companies",
            "pdf",
            tmp_path,
        )


# ============================================================
# CUSTOM SCREEN EXPORT
# ============================================================

def test_custom_screen_csv_export(
    tmp_path,
):
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

    path = export_custom_screen(
        filters,
        filename="custom",
        export_format="csv",
        directory=tmp_path,
    )

    assert path.exists()

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    assert len(rows) == 33


# ============================================================
# DATA INTEGRITY
# ============================================================

def test_export_preserves_rank():
    ranked = rank_companies()

    prepared = prepare_export_rows(
        ranked[:10]
    )

    assert [
        row["rank"]
        for row in prepared
    ] == list(
        range(1, 11)
    )


def test_export_preserves_company_id():
    ranked = rank_companies()

    prepared = prepare_export_row(
        ranked[0]
    )

    assert (
        prepared["company_id"]
        == ranked[0]["company_id"]
    )