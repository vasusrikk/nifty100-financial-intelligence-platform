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






## Sprint 5 - Intelligence & Automated Reports

### Objective

Sprint 5 implemented the financial-intelligence and automated-reporting layer of the NIFTY100 Financial Intelligence Platform.

The sprint introduced structured financial-text parsing, explainable Pros and Cons generation, cash-flow intelligence, capital-allocation analysis, and automated company PDF tear sheets.

### Analysis Parser

The financial Analysis workbook contains textual metrics that must be converted into structured analytical records.

The parser is implemented in:

`src/nlp/analysis_parser.py`

It processes:

- Compounded Sales Growth
- Compounded Profit Growth
- Stock Price CAGR
- ROE

Verified source coverage:

- Source companies: 5
- Parsed rows: 80
- Four metric types
- 16 normalized metric records per represented company

The source Analysis workbook itself contains only five companies. This is a source-data limitation and is not artificially expanded to the complete 92-company universe.

Main output:

`output/analysis_parsed.csv`

### Explainable Pros and Cons

Rule-based Pros and Cons generation is implemented in:

`src/nlp/pros_cons.py`

The engine contains:

- 12 explicit PRO rules
- 12 explicit CON rules
- Revenue-growth rules
- Profit-growth rules
- Stock-price-growth rules
- ROE rules

Generated signals preserve:

- Company identifier
- Signal type
- Rule identifier
- Metric
- Period
- Percentage value
- Human-readable explanation

Because the source Analysis workbook contains five companies, text-derived Pros and Cons are limited to those available source companies rather than fabricated for all 92 companies.

### Cash-Flow Intelligence

Cash-flow intelligence is implemented through the analytics layer.

Major functionality includes:

- CFO quality analysis
- Cash-flow KPI computation
- Financial-distress pattern analysis
- Structured cash-flow reporting

Verified analytical coverage reaches 91 companies where the required source financial information is available.

Main deliverable:

`output/cashflow_intelligence.xlsx`

### Capital-Allocation Intelligence

The capital-allocation layer evaluates company financial behavior using available operating, investment, financing, and balance-sheet information.

Main output:

`output/capital_allocation.csv`

Verified analytical coverage reaches 91 companies where the required source values are available.

### Automated Company Tear Sheets

Automated PDF reporting is implemented in:

`src/reports/tearsheet.py`

Batch generation is implemented in:

`src/reports/batch_generate.py`

The reports combine available company analytics into concise company-level financial tear sheets.

Final verified result:

- Total companies: 92
- Tear sheets generated: 92
- Tear sheets validated: 92
- Required two-page reports: 92 / 92
- Generation failures: 0

Output directory:

`reports/tearsheets/`

### Sprint 5 Final Result

Sprint 5 successfully completed the financial-intelligence and automated-reporting layer.

Detailed implementation history and QA evidence are maintained in:

`sprint5_retro.md`

---

## Sprint 6 - Advanced Analytics, API & Finalization

### Objective

Sprint 6 completed the advanced analytics, programmatic API, deployment-readiness, portfolio intelligence, final reporting, regression testing, and acceptance-validation layers of the platform.

### Company Clustering

Unsupervised company segmentation is implemented in:

`src/analytics/clustering.py`

Final verified results:

- Companies clustered: 92
- Analytical clusters: 5
- Cluster-label rows: 92

Output:

`output/cluster_labels.csv`

### Cluster Profiling

Cluster interpretation is implemented in:

`src/analytics/cluster_profiling.py`

Final output:

`output/cluster_profiles.csv`

Verified result:

- Cluster profiles: 5
- Output columns: 13

### Outlier Detection

The advanced analytics layer identifies unusual company observations within the financial universe.

Output:

`output/outlier_report.csv`

Verified result:

- Outliers identified: 11
- Output columns: 8

### Portfolio Statistics

Portfolio-level distribution statistics are stored in:

`output/portfolio_stats.csv`

The portfolio statistics cover 10 major KPIs and include:

- Observation count
- 10th percentile
- 25th percentile
- Median
- 75th percentile
- 90th percentile
- Mean
- Standard deviation

Verified result:

- Portfolio KPI rows: 10

### FastAPI REST API

The programmatic service layer is implemented under:

`src/api/`

Main application:

`src/api/main.py`

Company routes:

`src/api/routes/companies.py`

Analytics routes:

`src/api/routes/analytics.py`

The API provides access to:

- Company listings
- Company details
- Financial ratios
- Valuation analytics
- Stock-price information
- Company signals
- Sector analytics
- Cluster analytics
- Outlier analytics
- Portfolio statistics

The application also exposes OpenAPI-compatible documentation.

### API Deliverables

API integration artifacts include:

`openapi.json`

`postman_collection.json`

Dedicated API tests are implemented in:

`tests/api/test_api.py`

The tests cover successful requests as well as invalid companies, invalid sectors, invalid years, and invalid query parameters.

### Docker Support

Container configuration is provided through:

`Dockerfile`

`.dockerignore`

The application container uses Python 3.12 and launches the FastAPI service with Uvicorn on port 8000.

### Continuous Integration

Automated CI is configured in:

`.github/workflows/ci.yml`

The workflow:

1. Checks out the repository.
2. Configures Python 3.12.
3. Installs project dependencies.
4. Verifies critical imports.
5. Imports the FastAPI application.
6. Executes the complete automated test suite.

### Portfolio Summary Report

Portfolio-level PDF reporting is implemented in:

`src/reports/portfolio_summary.py`

Generated report:

`reports/portfolio/portfolio_summary.pdf`

Verified source KPI rows:

- 10

Portfolio summary QA status:

**PASS**

### Sector Reports

Sector-level PDF reporting is implemented in:

`src/reports/sector_reports.py`

Verified final results:

- Broad sectors: 10
- Companies represented: 92
- Sector PDFs generated: 10
- Valid sector PDFs: 10

Output directory:

'reports/sector/'

### Final Radar Coverage

Final radar-chart coverage:

- Companies: 92
- Radar charts: 92 / 92

### Automated Testing

The complete automated regression suite was executed with pytest.

Verified result:

**559 passed**

HTML test evidence:

`reports/pytest_report.html`

### Analyst Documentation

Final analyst documentation:

`docs/analyst_guide.pdf`

### Acceptance Checklist

The final Sprint 1-6 acceptance-checklist generator is implemented in:

`src/reports/acceptance_checklist.py`

Generated document:

`docs/acceptance_checklist.pdf`

Verified acceptance results:

- Core artifacts: 18 / 18
- Radar charts: 92 / 92
- Company tear sheets: 92 / 92
- Sector reports: 10 / 10
- Final acceptance status: PASS

Detailed Sprint 6 documentation is maintained in:

`sprint6_retro.md`

---

## Final Platform Architecture

The final workflow is:

```text
Raw Financial Data
        |
        v
ETL & Validation
        |
        v
SQLite Financial Database
        |
        v
Financial KPI Engines
        |
        +----------------------+
        |                      |
        v                      v
Screening & Ranking      Valuation Analytics
        |                      |
        +----------+-----------+
                   |
                   v
          Peer & Sector Analytics
                   |
        +----------+-----------+
        |                      |
        v                      v
Cash-Flow Intelligence   Pros / Cons Intelligence
        |                      |
        +----------+-----------+
                   |
                   v
         Advanced Analytics
     Clustering / Outliers /
       Portfolio Statistics
                   |
        +----------+-----------+
        |                      |
        v                      v
Streamlit Dashboard       FastAPI REST API
        |                      |
        +----------+-----------+
                   |
                   v
         Automated Reporting
 Company / Sector / Portfolio PDFs
                   |
                   v
        Final QA & Acceptance