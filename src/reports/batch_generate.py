"""Sprint 5 - Day 34: Batch PDF Generation and Validation.

Generates a two-page financial tearsheet for every company.

Outputs:
- reports/tearsheets/<COMPANY>_tearsheet.pdf
- logs/pdf_failures.log
- output/day34_pdf_validation.csv
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

from src.reports.tearsheet import generate_tearsheet


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

LOG_DIR = (
    PROJECT_ROOT
    / "logs"
)

FAILURE_LOG = (
    LOG_DIR
    / "pdf_failures.log"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "output"
)

VALIDATION_OUTPUT = (
    OUTPUT_DIR
    / "day34_pdf_validation.csv"
)


# ============================================================
# EXPECTED PDF CONFIGURATION
# ============================================================

EXPECTED_PAGE_COUNT = 2


# ============================================================
# SETUP
# ============================================================

def setup_directories():
    """Create required Day 34 directories."""

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def setup_failure_logger():
    """Configure the PDF failure logger."""

    logger = logging.getLogger(
        "day34_pdf_failures"
    )

    logger.setLevel(
        logging.ERROR
    )

    logger.handlers.clear()

    handler = logging.FileHandler(
        FAILURE_LOG,
        mode="w",
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(
        formatter
    )

    logger.addHandler(
        handler
    )

    return logger


# ============================================================
# COMPANY UNIVERSE
# ============================================================

def load_company_universe():
    """
    Load every company from the company master table.
    """

    query = """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        ORDER BY id
    """

    with sqlite3.connect(
        DB_PATH
    ) as connection:

        frame = pd.read_sql_query(
            query,
            connection,
        )

    frame["company_id"] = (
        frame["company_id"]
        .astype(str)
        .str.strip()
    )

    return frame


# ============================================================
# PDF VALIDATION
# ============================================================

def validate_pdf(
    pdf_path,
):
    """
    Validate one generated PDF.

    Checks:
    - File exists
    - File is not empty
    - PDF can be opened
    - Exactly two pages exist
    """

    pdf_path = Path(
        pdf_path
    )

    result = {
        "pdf_exists": False,
        "file_size_bytes": 0,
        "pdf_readable": False,
        "page_count": None,
        "page_count_valid": False,
        "validation_status": "FAILED",
        "validation_message": "",
    }

    if not pdf_path.exists():

        result[
            "validation_message"
        ] = "PDF file does not exist."

        return result

    result[
        "pdf_exists"
    ] = True

    file_size = (
        pdf_path.stat().st_size
    )

    result[
        "file_size_bytes"
    ] = file_size

    if file_size <= 0:

        result[
            "validation_message"
        ] = "PDF file is empty."

        return result

    try:

        reader = PdfReader(
            str(pdf_path)
        )

        page_count = len(
            reader.pages
        )

        result[
            "pdf_readable"
        ] = True

        result[
            "page_count"
        ] = page_count

        result[
            "page_count_valid"
        ] = (
            page_count
            == EXPECTED_PAGE_COUNT
        )

        if (
            page_count
            != EXPECTED_PAGE_COUNT
        ):

            result[
                "validation_message"
            ] = (
                "Unexpected page count: "
                f"{page_count}. "
                f"Expected: {EXPECTED_PAGE_COUNT}."
            )

            return result

        result[
            "validation_status"
        ] = "PASS"

        result[
            "validation_message"
        ] = (
            "PDF generated and validated."
        )

        return result

    except Exception as error:

        result[
            "validation_message"
        ] = (
            "PDF validation error: "
            f"{error}"
        )

        return result


# ============================================================
# GENERATE ONE COMPANY
# ============================================================

def generate_and_validate(
    company_id,
    company_name,
    logger,
):
    """
    Generate and validate one company tearsheet.
    """

    company_id = (
        str(company_id)
        .strip()
        .upper()
    )

    output_path = (
        REPORT_DIR
        / f"{company_id}_tearsheet.pdf"
    )

    row = {
        "company_id": company_id,
        "company_name": company_name,
        "pdf_path": str(
            output_path
        ),
        "generation_status": "FAILED",
        "pdf_exists": False,
        "file_size_bytes": 0,
        "pdf_readable": False,
        "page_count": None,
        "page_count_valid": False,
        "validation_status": "FAILED",
        "validation_message": "",
    }

    try:

        generated_path = (
            generate_tearsheet(
                company_id,
                output_path=output_path,
            )
        )

        row[
            "generation_status"
        ] = "PASS"

        validation = (
            validate_pdf(
                generated_path
            )
        )

        row.update(
            validation
        )

        if (
            validation[
                "validation_status"
            ]
            != "PASS"
        ):

            logger.error(
                "%s | %s | VALIDATION FAILURE | %s",
                company_id,
                company_name,
                validation[
                    "validation_message"
                ],
            )

        return row

    except Exception as error:

        message = (
            f"{type(error).__name__}: "
            f"{error}"
        )

        row[
            "validation_message"
        ] = message

        logger.error(
            "%s | %s | GENERATION FAILURE | %s",
            company_id,
            company_name,
            message,
            exc_info=True,
        )

        return row


# ============================================================
# BATCH GENERATOR
# ============================================================

def generate_all_tearsheets():
    """
    Generate and validate PDFs for the complete company
    universe.
    """

    setup_directories()

    logger = (
        setup_failure_logger()
    )

    companies = (
        load_company_universe()
    )

    results = []

    total = len(
        companies
    )

    print(
        "DAY 34 BATCH PDF GENERATION"
    )

    print(
        "=" * 60
    )

    print(
        "COMPANIES TO PROCESS:",
        total,
    )

    print()

    for (
        position,
        company,
    ) in enumerate(
        companies.itertuples(
            index=False
        ),
        start=1,
    ):

        company_id = (
            str(
                company.company_id
            )
            .strip()
            .upper()
        )

        company_name = (
            str(
                company.company_name
            )
        )

        print(
            f"[{position}/{total}] "
            f"{company_id} - "
            f"{company_name}"
        )

        result = (
            generate_and_validate(
                company_id,
                company_name,
                logger,
            )
        )

        results.append(
            result
        )

        if (
            result[
                "generation_status"
            ]
            == "PASS"
            and result[
                "validation_status"
            ]
            == "PASS"
        ):

            print(
                "    PASS | "
                f"{result['page_count']} pages"
            )

        else:

            print(
                "    FAIL | "
                f"{result['validation_message']}"
            )

    validation_frame = (
        pd.DataFrame(
            results
        )
    )

    validation_frame.to_csv(
        VALIDATION_OUTPUT,
        index=False,
    )

    return (
        companies,
        validation_frame,
    )


# ============================================================
# FINAL QA
# ============================================================

def print_final_summary(
    companies,
    validation,
):
    """
    Print Day 34 batch-generation QA summary.
    """

    total_companies = len(
        companies
    )

    generation_pass = int(
        (
            validation[
                "generation_status"
            ]
            == "PASS"
        ).sum()
    )

    generation_fail = (
        total_companies
        - generation_pass
    )

    validation_pass = int(
        (
            validation[
                "validation_status"
            ]
            == "PASS"
        ).sum()
    )

    validation_fail = (
        total_companies
        - validation_pass
    )

    valid_two_page = int(
        validation[
            "page_count_valid"
        ]
        .fillna(False)
        .sum()
    )

    existing_pdf_files = len(
        list(
            REPORT_DIR.glob(
                "*_tearsheet.pdf"
            )
        )
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "DAY 34 BATCH PDF GENERATION COMPLETE"
    )

    print(
        "=" * 60
    )

    print(
        "COMPANIES:",
        total_companies,
    )

    print(
        "GENERATION PASS:",
        generation_pass,
    )

    print(
        "GENERATION FAIL:",
        generation_fail,
    )

    print(
        "VALIDATION PASS:",
        validation_pass,
    )

    print(
        "VALIDATION FAIL:",
        validation_fail,
    )

    print(
        "VALID 2-PAGE PDFS:",
        valid_two_page,
    )

    print(
        "PDF FILES IN DIRECTORY:",
        existing_pdf_files,
    )

    print(
        "\nREPORT DIRECTORY:",
        REPORT_DIR,
    )

    print(
        "VALIDATION CSV:",
        VALIDATION_OUTPUT,
    )

    print(
        "FAILURE LOG:",
        FAILURE_LOG,
    )

    failed_rows = validation[
        validation[
            "validation_status"
        ]
        != "PASS"
    ]

    if failed_rows.empty:

        print(
            "\nDAY 34 STATUS: PASS"
        )

        print(
            "ALL COMPANY TEARSHEETS "
            "GENERATED AND VALIDATED."
        )

    else:

        print(
            "\nDAY 34 STATUS: "
            "REQUIRES FIXES"
        )

        print(
            "\nFAILED COMPANIES:"
        )

        for row in (
            failed_rows
            .itertuples(
                index=False
            )
        ):

            print(
                row.company_id,
                "|",
                row.validation_message,
            )


# ============================================================
# MAIN
# ============================================================

def main():
    """Run Sprint 5 Day 34."""

    (
        companies,
        validation,
    ) = generate_all_tearsheets()

    print_final_summary(
        companies,
        validation,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()