# NIFTY100 Financial Intelligence Platform

## Project Overview

The NIFTY100 Financial Intelligence Platform is an end-to-end financial analytics and intelligence system developed to transform structured company financial data into meaningful, explainable, and auditable financial insights.

The platform covers the complete workflow from raw financial-data ingestion to analytics, intelligence generation, interactive dashboards, and automated company PDF reports.

The project was developed across five sprints:

- Sprint 1 - Data Ingestion & ETL
- Sprint 2 - Financial Analytics Engine
- Sprint 3 - Peer Analytics & Dashboard
- Sprint 4 - Valuation, QA & Platform Enhancement
- Sprint 5 - Intelligence & Automated Reports

The final platform contains financial information for 92 companies and supports financial ratios, growth analysis, peer comparison, valuation analysis, cash-flow intelligence, NLP-based Pros and Cons, capital-allocation analysis, dashboards, and automated two-page company tear sheets.

---

## Sprint 1 - Data Ingestion & ETL

### Objective

Sprint 1 established the data foundation of the NIFTY100 Financial Intelligence Platform.

The objective was to ingest the supplied financial datasets, clean and normalise inconsistent fields, validate data quality, isolate invalid records, and load reliable financial information into a SQLite database.

### Data Sources

The ETL pipeline processes structured datasets covering:

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

### ETL Pipeline

The Sprint 1 processing flow is:

Raw Excel Files
-> Data Loading
-> Header Detection
-> Field Normalisation
-> Ticker Normalisation
-> Financial-Year Normalisation
-> Schema Validation
-> Data Quality Checks
-> Deduplication
-> Invalid Row Isolation
-> SQLite Loading
-> Load Audit

### Features Implemented

- Excel financial-data ingestion
- Header detection
- Column and field normalisation
- Company ticker normalisation
- Financial-year normalisation
- Schema validation
- Data-quality validation
- Duplicate detection and removal
- Foreign-key validation
- Rejected-row handling
- SQLite database loading
- Load auditing

### Main Sprint 1 Outputs

```text
nifty100.db
output/load_audit.csv
output/validation_failures.csv
output/rejected_rows.csv







## Sprint 2 - Financial Analytics Engine

### Objective

Sprint 2 transformed the cleaned financial data from Sprint 1 into structured financial KPIs and growth metrics.

The objective was to build reusable and transparent financial-analysis engines while explicitly handling missing values and financial edge cases.

### Financial Ratios Implemented

The platform calculates financial ratios including:

- Net Profit Margin (NPM)
- Operating Profit Margin (OPM)
- Return on Equity (ROE)
- Return on Capital Employed (ROCE)
- Return on Assets (ROA)
- Debt-to-Equity Ratio
- Interest Coverage Ratio (ICR)
- Net Debt
- Asset Turnover

### CAGR Engine

Growth calculations were implemented for:

- Revenue CAGR
- PAT CAGR
- EPS CAGR

The CAGR engine supports multiple analysis windows, including:

- 3-Year CAGR
- 5-Year CAGR
- 10-Year CAGR

### CAGR Edge Cases

The CAGR engine does not apply the normal CAGR formula blindly.

Financial conditions are explicitly classified using flags such as:

```text
NORMAL
DECLINE_TO_LOSS
TURNAROUND
BOTH_NEGATIVE
ZERO_BASE
INSUFFICIENT


CapEx Data Limitation
The supplied database does not contain a reliable explicit CapEx field.
Investing cash flow is not automatically treated as CapEx because investing activity may contain:
- Acquisitions
- Investments
- Asset disposals
- Other investing cash flows
Therefore, CapEx-dependent KPIs are explicitly marked as:
CAPEX_SOURCE_UNAVAILABLE

instead of fabricating financial values.
Financial Ratios Database
Calculated metrics are stored in the analytical database table:
financial_ratios

Important fields include:
npm_pct
opm_pct
roe_pct
roce_pct
roa_pct
de_ratio
icr
net_debt
asset_turnover
revenue_cagr_5yr
pat_cagr_5yr
eps_cagr_5yr
cfo_margin_pct
cfo_pat_ratio
fcf
fcf_margin_pct
capex_sales_pct







## Sprint 3 - Peer Analytics & Dashboard

### Objective

Sprint 3 transformed the financial analytics engine into a comparative and interactive financial intelligence platform.

The objective was to allow users to evaluate companies not only individually but also relative to their peers and sectors through analytical comparisons and an interactive Streamlit dashboard.

### Peer Analytics

Peer-analysis functionality was developed to compare companies using important financial metrics.

The peer analytics layer includes:

- Company-to-company comparison
- Sector-based comparison
- Financial ratio comparison
- Profitability comparison
- Growth comparison
- Leverage comparison
- Peer percentile analysis

### Peer Percentiles

Financial metrics are converted into comparative peer percentiles where applicable.

Peer percentile information is stored in:

```text
peer_percentiles

Main Sprint 3 Modules
Important analytics modules include:
src/analytics/peer.py
src/analytics/peer_comparison.py
src/analytics/profitability.py
src/analytics/radar.py
src/analytics/validate_kpis.py

Dashboard components are located under:
src/dashboard/

Sprint 3 Database Integration
The dashboard reads structured information from the central:
nifty100.db





## Sprint 4 - Valuation, QA & Platform Enhancement

### Objective

Sprint 4 expanded the platform with valuation intelligence, reporting improvements, and quality-assurance activities.

The objective was to evaluate company valuation using market-based financial multiples while maintaining sector context and validating the overall analytics and dashboard implementation.

### Valuation Analytics

The valuation engine analyses important market valuation metrics including:

- Price-to-Earnings Ratio (P/E)
- Price-to-Book Ratio (P/B)
- EV/EBITDA
- Dividend Yield
- Market Capitalisation
- Enterprise Value

### Sector-Relative Valuation

Companies from different industries can naturally trade at different valuation multiples.

Therefore, valuation metrics are compared against sector medians rather than applying one universal threshold to every company.

The valuation engine calculates sector medians for:

```text
P/E
P/B
EV/EBITDA


Main Sprint 4 Modules
Important files include:
src/analytics/valuation.py
src/analytics/sprint3_audit.py
src/dashboard/pages/01_home.py
src/dashboard/pages/02_profile.py
src/dashboard/pages/08_reports.py
src/dashboard/utils/db.py

Sprint 4 Supporting Outputs
Sprint 4 generated and maintained supporting analytical outputs including:
output/valuation_flags.csv
dashboard_qa.md


## Step 5 — Sprint 5: Intelligence & Automated Reports

Immediately underneath Sprint 4, paste:

```markdown
## Sprint 5 - Intelligence & Automated Reports

### Objective

Sprint 5 completed the financial intelligence and automated reporting layer of the NIFTY100 Financial Intelligence Platform.

The sprint introduced structured financial-text parsing, explainable Pros and Cons generation, cash-flow quality analysis, financial-distress detection, capital-allocation intelligence, and automated company PDF tear sheets.

---

### Day 29 - Analysis Parser

The Analysis workbook contains financial information represented as text, such as growth percentages associated with different periods.

The Day 29 parser converts these values into structured analytical records.

The parser processes metrics including:

- Compounded Sales Growth
- Compounded Profit Growth
- Stock Price CAGR
- ROE

The parser extracts:

- Metric type
- Period
- Percentage value
- Company identifier

### Day 29 Validation Results

```text
Parsed rows: 80
Companies: 5
Parse failures: 0
CAGR validations: 30
Validation pass: 23
Manual review: 1
Not comparable: 6

nifty100.db

output/analysis_parsed.csv
output/pros_cons.csv
output/cfo_quality_score.csv
output/cashflow_distress_flags.csv
output/capital_allocation_matrix.csv
output/cashflow_intelligence.xlsx
output/day34_pdf_validation.csv

reports/valuation_summary.xlsx
reports/tearsheets/

logs/pdf_failures.log







