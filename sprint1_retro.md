# Sprint 1 Retrospective — Data Foundation

## Sprint
Sprint 1 — Days 01–07

## Objective
Build the data foundation for the Nifty 100 Financial Intelligence
Platform by ingesting, normalising, validating, deduplicating and
loading the supplied financial datasets into SQLite.

## Work Completed

### D01 — Project Setup
- Created the required project directory structure.
- Created and activated the Python virtual environment.
- Installed project dependencies.
- Created `requirements.txt`.
- Created `.env` for local configuration.
- Created `.env.template` for reusable environment configuration.

### D02 — Excel Ingestion and Normalisation
- Implemented Excel loading for the supplied datasets.
- Added `header=1` handling for the 7 core Excel files.
- Implemented ticker normalisation using strip and uppercase rules.
- Implemented financial-year normalisation.
- Standardised company identifiers across datasets.

### D03 — Data Quality Validation
- Implemented the project DQ validation framework.
- Generated `output/validation_failures.csv`.
- Validation report includes:
  - rule
  - table
  - company_id
  - year
  - field
  - issue
  - severity
- Source-data violations were retained in the validation evidence
  rather than silently corrected.

### D04 — SQLite Schema and Loader
- Created `db/schema.sql`.
- Created `db/loader.py`.
- Enabled SQLite foreign-key constraints.
- Built the Module 1 10-table database.

### D05 — Full Data Load
- Processed all supplied core and supplementary datasets.
- Generated `nifty100.db`.
- Generated `output/load_audit.csv`.
- Generated `output/rejected_rows.csv`.
- Load audit records:
  - table
  - rows_in
  - rows_out
  - rejected
  - timestamp
  - runtime_s
### D06 — Manual Data Quality Review

The five companies specified in the Sprint 1 requirements were manually
reviewed across Profit & Loss, Balance Sheet, and Cash Flow:

| Company | P&L Rows | Balance Sheet Rows | Cash Flow Rows |
|---|---:|---:|---:|
| TCS | 12 | 13 | 12 |
| RELIANCE | 12 | 13 | 12 |
| HDFCBANK | 12 | 12 | 12 |
| INFY | 12 | 13 | 12 |
| ICICIBANK | 12 | 12 | 12 |

Three recent periods were spot-checked for each company across the
three core financial statements.

Observations:

- All five required companies have P&L, Balance Sheet, and Cash Flow data.
- TCS, RELIANCE, and INFY contain an additional 2024-09 Balance Sheet observation.
- Negative cash-flow values found in some periods were retained because
  negative cash flow is not by itself an ETL error.
- No financial values were fabricated or manually altered during review.
- Detailed evidence and observations are recorded in
  `manual_check_notes.md`.

### D07 — Exploratory SQL
Created `exploratory_queries.sql` containing 20 exploratory queries
covering:
- table row counts
- null-value checks
- year distributions
- company history coverage
- missing data coverage
- sector mappings
- orphan checks
- time-series coverage

## Verification Results

Final database verification:

- SQLite table count: 10
- Company master records: 92
- Foreign-key violations: 0
- P&L duplicate `(company_id, year)` pairs: 0
- Balance Sheet duplicate `(company_id, year)` pairs: 0
- Cash Flow duplicate `(company_id, year)` pairs: 0

## Data Quality Findings

The supplied raw datasets contain genuine data-quality issues.

The validator reported:

- Total validation findings: 1530
- CRITICAL: 786
- WARNING: 744

Critical findings include duplicate records, company identifiers
without matching company-master records, and unparseable financial
year values.

These findings were logged and handled according to the ETL/DQ
workflow rather than hidden or fabricated.

## What Went Well

- All supplied datasets could be ingested through the ETL pipeline.
- Ticker and year normalisation were automated.
- Critical invalid records were isolated before database insertion.
- Foreign-key integrity passed after loading.
- Duplicate annual records were removed from the cleaned database.
- Audit and validation evidence is reproducible.

## Issues Identified

- Some source company IDs are absent from the company master.
- Some financial-year values cannot be parsed normally.
- Some companies have incomplete historical coverage.
- The raw reference dataset still contains CRITICAL DQ findings that
  require formal review/acceptance rather than silent modification.

## Sprint 1 Outcome

The Module 1 Data Ingestion & ETL pipeline has been implemented and
the cleaned SQLite database passes structural, duplicate and
foreign-key checks.

Formal Sprint 1 acceptance of the remaining source-data DQ exceptions
requires the documented review/clearance process.