# Sprint 2 Retrospective — Financial Ratio Engine

**Project:** NIFTY 100 Financial Analytics  
**Sprint:** Sprint 2 — Financial Ratio Engine  
**Date:** 24-09-2026

---

## 1. Sprint Objective

The objective of Sprint 2 was to transform the cleaned financial data produced during Sprint 1 into a reliable, tested and database-integrated financial-ratio analytics layer.

The sprint covered:

- Profitability ratios
- Leverage and efficiency ratios
- CAGR calculations
- Cash-flow KPIs
- Financial-sector-specific handling
- Ratio cross-validation
- Edge-case and anomaly management
- Consolidated financial-ratios database population
- Automated KPI testing
- Screener validation
- Final Sprint QA

---

## 2. Day 08 — Profitability Ratios

Implemented:

- Net Profit Margin (NPM)
- Operating Profit Margin (OPM)
- Return on Equity (ROE)
- Return on Capital Employed (ROCE)
- Return on Assets (ROA)
- OPM source cross-validation
- Financial-sector identification

Rows processed: **1070**

### KPI Availability

- NPM: 1069
- OPM: 1057
- ROE: 1055
- ROCE: 1043
- ROA: 1054

### OPM Source Cross-Check

- PASS: 854
- MISMATCH: 216

The calculated ratio-engine values remain the analytical values. Source values are used for validation rather than silently replacing calculated results.

Output:

`output/day08_profitability_ratios.csv`

**Status: COMPLETE**

---

## 3. Day 09 — Leverage and Efficiency

Implemented:

- Debt-to-Equity Ratio
- Interest Coverage Ratio
- Leverage classification
- Interest coverage classification
- Asset Turnover
- Net Debt source validation
- Financial-sector D/E carve-out

Rows processed: **1070**

### KPI Availability

- Debt-to-Equity: 1055
- Interest Coverage Ratio: 1027
- Asset Turnover: 1054
- Net Debt: 0

### Leverage Classifications

- NORMAL: 725
- SECTOR_RELATIVE: 258
- HIGH_LEVERAGE: 87

### Interest Coverage Classifications

- NORMAL: 844
- ICR_WARNING: 135
- DEBT_FREE: 91

### Financial-Sector Handling

Conventional Debt-to-Equity thresholds are not applied directly to Financial-sector observations because structurally higher leverage is normal for banks and other financial institutions.

Financial-sector observations therefore use:

`SECTOR_RELATIVE`

### Net Debt Limitation

Net Debt requires:

`Borrowings - Cash/Cash Equivalents`

The supplied dataset does not contain a dedicated cash or cash-equivalent field.

Therefore Net Debt was deliberately not fabricated.

Status:

`SOURCE_CASH_FIELD_UNAVAILABLE`

Output:

`output/day09_leverage_efficiency.csv`

**Status: COMPLETE WITH DOCUMENTED SOURCE LIMITATION**

---

## 4. Day 10 — CAGR Engine

Implemented CAGR calculations for:

### Revenue

- 3-Year CAGR
- 5-Year CAGR
- 10-Year CAGR

### PAT

- 3-Year CAGR
- 5-Year CAGR
- 10-Year CAGR

### EPS

- 3-Year CAGR
- 5-Year CAGR
- 10-Year CAGR

The CAGR engine uses actual fiscal-year endpoints rather than assuming that adjacent row positions represent the required time interval.

Implemented edge-case classifications:

- NORMAL
- DECLINE_TO_LOSS
- TURNAROUND
- BOTH_NEGATIVE
- ZERO_BASE
- INSUFFICIENT

### 5-Year CAGR Availability

- Revenue CAGR: 612
- PAT CAGR: 549
- EPS CAGR: 545

### Day 10 Unit Tests

**10 tests passed, 0 failed**

Output:

`output/day10_cagr.csv`

**Status: COMPLETE**

---

## 5. Day 11 — Cash Flow KPIs

Implemented:

- CFO Margin
- CFO/PAT
- CFO/PAT edge-case classification
- Free Cash Flow formula support
- FCF Margin formula support
- Capex/Sales formula support
- Explicit source-availability handling

Rows processed: **1056**

### KPI Availability

- CFO Margin: 1050
- CFO/PAT: 1050
- FCF: 0
- FCF Margin: 0
- Capex/Sales: 0

### CFO/PAT Classifications

- NORMAL: 990
- NEGATIVE_PAT: 60
- MISSING: 5
- ZERO_PAT: 1

### Capex Limitation

The supplied source data does not contain a dedicated Capex field.

Therefore the following KPIs cannot be reliably populated from the available production data:

- Free Cash Flow
- FCF Margin
- Capex/Sales

The aggregate `investing_activity` field was intentionally not treated as Capex because investing cash flow can contain acquisitions, investments, asset disposals and other non-Capex transactions.

Status:

`CAPEX_SOURCE_UNAVAILABLE`

Outputs:

`output/day11_cashflow_kpis.csv`

`output/capital_allocation.csv`

### Day 11 Unit Tests

**14 tests passed, 0 failed**

**Status: COMPLETE WITH DOCUMENTED SOURCE LIMITATION**

---

## 6. Day 12 — Consolidated Financial Ratios Database

Created and populated:

`financial_ratios`

The original implementation used Day 08/P&L as the company-year base and produced only 1070 rows.

Database investigation established:

- P&L rows: 1070
- Balance Sheet rows: 1140
- Cash Flow rows: 1056
- Unique company-year combinations across P&L + Balance Sheet + Cash Flow: **1155**
- Balance Sheet periods without matching P&L periods: **85**

The Day 12 population engine was therefore corrected to construct the company-year universe using the SQL-equivalent union of:

- `profitandloss`
- `balancesheet`
- `cashflow`

KPI outputs are then left-joined onto this legitimate company-year universe.

No financial observations were fabricated to satisfy the row-count requirement.

### Final Day 12 Results

- Company-year base rows: **1155**
- Rows inserted: **1155**
- Minimum required: **1100**
- Row-count requirement: **PASS**
- Duplicate company-year pairs: **0**
- Uniqueness: **PASS**
- Foreign-key integrity: **PASS**

Foreign-key relationship:

`financial_ratios.company_id -> companies.id`

### Final KPI Availability

- NPM: 1069
- OPM: 1057
- ROE: 1055
- ROCE: 1043
- ROA: 1054
- Debt-to-Equity: 1055
- Interest Coverage Ratio: 1027
- Asset Turnover: 1054
- Revenue 5Y CAGR: 612
- PAT 5Y CAGR: 549
- EPS 5Y CAGR: 545
- CFO Margin: 1050
- CFO/PAT: 1050
- FCF: 0
- FCF Margin: 0
- Capex/Sales: 0

Missing KPI values remain SQL `NULL` where the required source information is unavailable.

**Status: COMPLETE — 1155 LEGITIMATE COMPANY-YEAR ROWS**

---

## 7. Day 13 — Bank ROCE Carve-Out & Edge-Case Review

Day 13 implemented dedicated ratio cross-validation and anomaly logging.

Output:

`output/ratio_edge_cases.log`

### Financial-Sector Review

The current loaded `sectors` dataset contains:

- Unique Financial-sector companies: **23**
- Financial-sector company-year observations: **272**
- D/E `SECTOR_RELATIVE` carve-out rows: **258**

The Sprint reference material expected 19 Financial-sector companies, while the loaded dataset contains 23.

The implementation retains the actual loaded source classification rather than deleting or reclassifying companies solely to reproduce the reference count.

This is documented as a source/version difference.

### ROCE Cross-Validation

Calculated ROCE was compared against:

`companies.roce_percentage`

Differences greater than **5 percentage points** were logged.

Result:

- ROCE anomalies > 5 percentage points: **576**

### ROE Cross-Validation

Calculated ROE was compared against:

`companies.roe_percentage`

Result:

- ROE anomalies > 5 percentage points: **528**

Calculated ratio-engine values remain the analytics values. Source ratios are used as reference cross-checks.

### Anomaly Classification

Logged anomalies were classified into diagnostic categories:

- DATA_SOURCE_ISSUE: 12
- VERSION_DIFFERENCE: 449
- FORMULA_DISCREPANCY: 643

These categories are diagnostic review classifications and do not silently modify the underlying source data or calculated KPI values.

### Important Source-Ratio Limitation

`companies.roe_percentage` and `companies.roce_percentage` are company-level reference fields and do not contain a fiscal-year dimension.

They are therefore suitable for reference cross-validation but cannot be assumed to represent every historical company-year observation.

**Status: COMPLETE WITH DOCUMENTED SOURCE/VERSION DIFFERENCES**

---

## 8. Day 14 — Testing, Screener Validation & Sprint Review

### Complete KPI Regression Suite

Final command:

`python -m pytest tests\kpi -q`

Result:

**55 tests passed, 0 failed**

The test suite covers:

- NPM
- OPM
- OPM validation
- ROE
- ROCE
- ROA
- Financial-sector identification
- Debt-to-Equity
- Financial-sector leverage carve-out
- Interest Coverage Ratio
- Interest coverage warnings
- Debt-free handling
- Net Debt formula behavior
- Asset Turnover
- CAGR calculations
- CAGR edge cases
- CFO Margin
- CFO/PAT
- CFO/PAT classifications
- FCF formula behavior
- FCF Margin behavior
- Capex/Sales behavior
- Financial-sector ROCE benchmarking

### Screener Validation

Required screener:

`ROE > 15% AND D/E < 1`

Counting a company if it met the condition in any historical year produced:

**59 companies**

That interpretation mixes historical observations and is not appropriate for a current screener preview.

Using each company's **latest available company-year observation** produced:

**38 companies**

Expected Sprint range:

**15–50 companies**

Result:

**PASS**

### Screener Data Review

Manual review identified extreme calculated ROE observations requiring source-data investigation.

Examples include:

- BEL 2024-03: ROE 4744.05%
- HAL 2024-03: ROE 3816.58%
- INDIGO 2024-03: ROE 892.57%

The calculations were traced back to the stored source values.

Examples:

- BEL: Net Profit = 3985; Equity Capital + Reserves = 84
- HAL: Net Profit = 7595; Equity Capital + Reserves = 199
- INDIGO: Net Profit = 8167; Equity Capital + Reserves = 915

The implemented ROE formula therefore reproduces the values implied by the stored database fields.

The ratio formula was **not altered, capped or manipulated** to hide these observations.

### Extreme ROE QA Counts

Across the populated ratio table:

- ROE > 100%: **51 rows**
- ROE > 500%: **29 rows**
- ROE > 1000%: **27 rows**
- ROE < -100%: **7 rows**

These observations are treated as upstream source/unit-scale or financial-data review cases requiring further validation.

**Status: COMPLETE WITH SOURCE-DATA ANOMALIES DOCUMENTED**

---

## 9. What Went Well

1. Sprint 1's cleaned SQLite database was successfully reused as the analytical foundation.

2. Financial formulas were separated into reusable and independently testable functions.

3. The KPI engine protects against zero and invalid denominators.

4. Financial-sector leverage receives separate treatment rather than inappropriate universal D/E thresholds.

5. CAGR calculations handle actual fiscal-year intervals and explicitly classify loss, turnaround, zero-base and insufficient-history cases.

6. The consolidated `financial_ratios` table contains **1155 legitimate company-year observations**.

7. Duplicate `(company_id, year)` pairs remain at **0**.

8. Foreign-key integrity passes successfully.

9. The complete KPI regression suite reached **55 passing tests with 0 failures**.

10. Missing Cash and Capex fields were documented rather than replaced with unsupported assumptions.

11. Day 13 introduced explicit source-vs-calculated ratio cross-validation.

12. Day 14 manual review successfully exposed extreme source-data/unit-scale anomalies rather than allowing them to pass unnoticed.

13. The latest-period screener produced **38 companies**, within the required 15–50 validation range.

---

## 10. Challenges Encountered

### Missing Cash/Cash-Equivalent Field

A dedicated cash/cash-equivalent value is unavailable.

Reliable Net Debt therefore cannot currently be populated.

### Missing Capex Field

A dedicated Capex field is unavailable.

Reliable production values for:

- FCF
- FCF Margin
- Capex/Sales

cannot currently be populated.

### Source Ratio Versioning

The reference ROE and ROCE values stored in `companies` are not year-specific.

Historical calculated company-year ratios therefore cannot always be directly compared with these company-level reference values.

### Financial-Sector Count Difference

The Sprint reference expected 19 Financial-sector companies.

The current loaded source classification contains **23**.

The source data was preserved instead of manipulating classifications to match the reference count.

### Extreme ROE Observations

Several source Balance Sheet equity/reserve values produce unusually large calculated ROE values.

The formula itself reproduces the stored values correctly, so these observations require upstream source/unit-scale review rather than formula manipulation.

### Historical Coverage

Not every company contains continuous 3-year, 5-year or 10-year history.

The CAGR engine therefore returns `INSUFFICIENT` when the required endpoint is unavailable.

---

## 11. What Could Be Improved

1. Obtain a dedicated Cash/Cash Equivalents field to enable Net Debt.

2. Obtain dedicated Capex data to enable FCF, FCF Margin and Capex/Sales.

3. Validate source units and scaling for Balance Sheet equity/reserve fields associated with extreme ROE observations.

4. Store source ROE and ROCE by fiscal year so calculated and reference ratios can be compared on a like-for-like basis.

5. Reconcile the Financial-sector membership difference between the current dataset and Sprint reference data.

6. Increase historical coverage to improve 10-year CAGR availability.

7. Expand integration testing around the complete analytics pipeline.

8. Add automated CI execution of the complete KPI test suite.

9. Add configurable outlier detection for ratios such as ROE, ROCE, D/E and CFO/PAT.

10. Preserve anomaly evidence in a structured CSV/database audit table in addition to the human-readable log.

---

## 12. Sprint Acceptance Summary

| Checkpoint | Result |
|---|---|
| Profitability engine | PASS |
| Leverage engine | PASS |
| Efficiency engine | PASS |
| CAGR engine | PASS |
| Cash-flow engine | PASS WITH SOURCE LIMITATIONS |
| Financial-sector D/E handling | PASS |
| ROE/ROCE cross-validation | PASS |
| financial_ratios population | 1155 ROWS |
| Minimum 1100-row requirement | PASS |
| Duplicate company-year pairs | 0 |
| Foreign-key integrity | PASS |
| KPI regression tests | 55 PASSED, 0 FAILED |
| Latest-period screener | 38 COMPANIES |
| Screener expected range | PASS — 15 TO 50 |
| Edge-case log | GENERATED |
| Missing-data fabrication | NONE |

### Source-Data Limitations

Net Debt cannot be reliably calculated because the supplied source does not contain a dedicated cash/cash-equivalent field.

FCF, FCF Margin and Capex/Sales cannot be reliably populated because the supplied source does not contain a dedicated Capex field.

Extreme ROE observations have also exposed potential source-unit/scaling issues in some Balance Sheet equity/reserve observations.

These limitations were preserved and documented rather than hidden through artificial values or unsupported assumptions.

---

## 13. Sprint Outcome

Sprint 2 successfully delivered the Financial Ratio Engine and consolidated analytical database layer.

The implementation now contains:

- Tested profitability formulas
- Leverage and efficiency calculations
- Multi-window CAGR calculations
- Cash-flow KPIs
- Explicit edge-case classifications
- Financial-sector-specific leverage handling
- ROE and ROCE source cross-validation
- Consolidated financial-ratio storage
- Automated KPI regression tests
- Latest-period screener validation
- Edge-case logging
- Documented source-data limitations

The final `financial_ratios` table contains **1155 unique company-year records**, with:

- **0 duplicate company-year pairs**
- **PASS foreign-key integrity**
- **55 KPI tests passed**
- **0 KPI test failures**
- **38 latest-period screener matches**
- **No fabricated Cash or Capex-derived metrics**

Remaining anomalies relate primarily to source availability, source versioning and potential source-unit/scaling issues rather than hidden modifications to financial calculations.

**Sprint 2 Review Status: COMPLETE WITH DOCUMENTED SOURCE-DATA LIMITATIONS**