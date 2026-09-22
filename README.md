# Nifty 100 Financial Intelligence Platform

## Sprint 1 — Data Ingestion & ETL

This repository contains the Sprint 1 Data Ingestion and ETL implementation for the **Nifty 100 Financial Intelligence Platform**.

The objective of Sprint 1 is to build a reliable data foundation by ingesting the 12 supplied structured financial datasets, normalising inconsistent fields, validating data quality, removing duplicate records, and loading cleaned data into SQLite for downstream financial analytics.

---

## Core Platform Deliverable

### Data Ingestion

The ETL pipeline processes **12 structured datasets**, covering:

1. Companies
2. Profit & Loss
3. Balance Sheet
4. Cash Flow
5. Analysis
6. Documents
7. Pros & Cons
8. Sectors
9. Stock Prices
10. Market Capitalisation
11. Financial Ratios
12. Peer Groups

The datasets include company master information, financial statements, market information, sector classifications, historical prices and supplementary analytics data.

---

## ETL Pipeline

The Sprint 1 pipeline follows:

Excel Files
→ Data Loading
→ Header Detection
→ Field Normalisation
→ Ticker Normalisation
→ Financial Year Normalisation
→ Schema Validation
→ Data Quality Checks
→ Deduplication
→ Invalid Row Isolation
→ SQLite Loading
→ Load Audit

---

## Features Implemented

### Excel Ingestion

- Reads all supplied Excel datasets
- Supports core files containing title/header rows
- Converts Excel data into pandas DataFrames
- Handles differences between core and supplementary file structures

### Ticker Normalisation

Company identifiers are standardised using trimming and uppercase conversion.

Example:

`" tcs "` → `"TCS"`

This provides consistent company identifiers across financial tables.

### Financial Year Normalisation

Financial-year labels are converted into consistent machine-readable representations.

Example:

`Mar-23` → `2023-03`

Invalid or unsupported financial-year values are identified by the validation pipeline.

### Data Quality Validation

A rule-based validator checks the supplied datasets for data-quality problems.

Validation findings are written to:

`output/validation_failures.csv`

The report includes:

- Rule
- Table
- Company ID
- Year
- Field
- Issue
- Severity

Severity levels include:

- CRITICAL
- WARNING

Source-data problems are recorded rather than silently hidden or fabricated.

### Deduplication

Duplicate annual financial records are detected using company and financial-year identifiers.

Final verification produced:

- Profit & Loss duplicate company-year pairs: **0**
- Balance Sheet duplicate company-year pairs: **0**
- Cash Flow duplicate company-year pairs: **0**

### Foreign-Key Validation

Company identifiers are checked against the company master before valid records are loaded.

Final SQLite verification:

`PRAGMA foreign_key_check` → **PASS**

### Rejected Row Handling

Records failing critical loading requirements are isolated for review.

Rejected records are stored in:

`output/rejected_rows.csv`

This preserves traceability between source data and the cleaned analytical database.

---

## SQLite Database

The ETL process generates:

`nifty100.db`

### Module 1 Database Tables

The Sprint 1 database contains 10 operational tables:

1. companies
2. profitandloss
3. balancesheet
4. cashflow
5. analysis
6. documents
7. prosandcons
8. sectors
9. market_cap
10. stock_prices

The supplementary datasets are also processed by the ingestion workflow and are available for subsequent analytics modules.

---

## Verified Sprint 1 Results

| Check | Result |
|---|---|
| Structured datasets processed | 12 |
| Companies in master dataset | 92 |
| SQLite operational tables | 10 |
| Foreign-key integrity | PASS |
| P&L duplicate company-year records | 0 |
| Balance Sheet duplicate company-year records | 0 |
| Cash Flow duplicate company-year records | 0 |
| Load audit generated | PASS |
| Validation report generated | PASS |
| Rejected-row report generated | PASS |
| Exploratory SQL created | PASS |

---

## Data Quality Findings

The supplied source datasets contain data-quality exceptions.

The validation engine detected issues including:

- duplicate records
- company identifiers missing from the company master
- unparseable financial-year values
- missing values
- financial consistency anomalies

These issues are retained in the QA outputs instead of being silently modified.

This allows the cleaned analytical database and the original data-quality evidence to remain independently auditable.

---

## Load Audit

The ETL process generates:

`output/load_audit.csv`

The audit contains:

- `table`
- `rows_in`
- `rows_out`
- `rejected`
- `timestamp`
- `runtime_s`

This provides per-table evidence of the ingestion process.

---

## Project Structure

```text
nifty100_project/
│
├── config/
├── data/
├── db/
│   ├── schema.sql
│   └── loader.py
│
├── docs/
├── notebooks/
│
├── output/
│   ├── load_audit.csv
│   ├── validation_failures.csv
│   └── rejected_rows.csv
│
├── reports/
│
├── src/
│   ├── analytics/
│   ├── api/
│   ├── dashboard/
│   ├── etl/
│   │   ├── loader.py
│   │   ├── normaliser.py
│   │   └── validator.py
│   └── reports/
│
├── tests/
│   └── etl/
│       └── test_normalise.py
│
├── .env.template
├── .gitignore
├── exploratory_queries.sql
├── nifty100.db
├── requirements.txt
├── sprint1_retro.md
└── README.md