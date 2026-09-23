\# Sprint 2 Retrospective — Financial Ratio Engine



\*\*Project:\*\* NIFTY 100 Financial Analytics  

\*\*Sprint:\*\* Sprint 2 — Financial Ratio Engine  

\*\*Date:\*\* 23-09-2026



\---



\## 1. Sprint Objective



The objective of Sprint 2 was to transform the cleaned financial data produced during Sprint 1 into a reliable financial-ratio analytics layer.



The sprint covered:



\- Profitability ratios

\- Leverage and efficiency ratios

\- CAGR calculations

\- Cash-flow KPIs

\- Financial-sector-specific handling

\- Edge-case management

\- Consolidated financial-ratios database population

\- Automated testing and final validation



\---



\## 2. Day 08 — Profitability Ratios



Implemented:



\- Net Profit Margin (NPM)

\- Operating Profit Margin (OPM)

\- Return on Equity (ROE)

\- Return on Capital Employed (ROCE)

\- Return on Assets (ROA)



Rows processed: \*\*1070\*\*



KPI availability:



\- NPM: 1069

\- OPM: 1057

\- ROE: 1055

\- ROCE: 1043

\- ROA: 1054



OPM source cross-check:



\- PASS: 854

\- MISMATCH: 216



Financial-sector rows identified: \*\*258\*\*



Output:



`output/day08\_profitability\_ratios.csv`



\*\*Status: COMPLETE\*\*



\---



\## 3. Day 09 — Leverage and Efficiency



Implemented:



\- Debt-to-Equity Ratio

\- Interest Coverage Ratio

\- Leverage classification

\- Interest coverage classification

\- Asset Turnover

\- Net Debt source validation



Rows processed: \*\*1070\*\*



KPI availability:



\- Debt-to-Equity: 1055

\- Interest Coverage Ratio: 1027

\- Asset Turnover: 1054



Leverage classifications:



\- NORMAL: 725

\- SECTOR\_RELATIVE: 258

\- HIGH\_LEVERAGE: 87



Interest Coverage classifications:



\- NORMAL: 844

\- ICR\_WARNING: 135

\- DEBT\_FREE: 91



\### Net Debt Limitation



Net Debt requires:



`Borrowings - Cash/Cash Equivalents`



The supplied dataset does not contain a dedicated cash or cash-equivalent field.



Therefore Net Debt was not fabricated.



Status used:



`SOURCE\_CASH\_FIELD\_UNAVAILABLE`



Output:



`output/day09\_leverage\_efficiency.csv`



\*\*Status: COMPLETE WITH DOCUMENTED SOURCE LIMITATION\*\*



\---



\## 4. Day 10 — CAGR Engine



Implemented CAGR for:



\### Revenue

\- 3-Year CAGR

\- 5-Year CAGR

\- 10-Year CAGR



\### PAT

\- 3-Year CAGR

\- 5-Year CAGR

\- 10-Year CAGR



\### EPS

\- 3-Year CAGR

\- 5-Year CAGR

\- 10-Year CAGR



The CAGR engine uses actual fiscal-year endpoints rather than blindly using row positions.



Implemented CAGR edge cases:



\- NORMAL

\- DECLINE\_TO\_LOSS

\- TURNAROUND

\- BOTH\_NEGATIVE

\- ZERO\_BASE

\- INSUFFICIENT



5-Year CAGR availability:



\- Revenue CAGR: 612

\- PAT CAGR: 549

\- EPS CAGR: 545



Output:



`output/day10\_cagr.csv`



\*\*Status: COMPLETE\*\*



\---



\## 5. Day 11 — Cash Flow KPIs



Implemented:



\- CFO Margin

\- CFO/PAT

\- CFO/PAT edge-case classifications



Rows processed: \*\*1056\*\*



Availability:



\- CFO Margin: 1050

\- CFO/PAT: 1050



CFO/PAT classifications:



\- NORMAL: 995

\- NEGATIVE\_PAT: 60

\- ZERO\_PAT: 1



\### Capex Limitation



The required source data does not contain a dedicated Capex field.



Therefore the following KPIs could not be calculated reliably:



\- Free Cash Flow

\- FCF Margin

\- Capex/Sales



The aggregate `investing\_activity` field was intentionally not treated as Capex because investing cash flow may contain transactions other than capital expenditure.



Status used:



`CAPEX\_SOURCE\_UNAVAILABLE`



Output:



`output/day11\_cashflow\_kpis.csv`



\*\*Status: COMPLETE WITH DOCUMENTED SOURCE LIMITATION\*\*



\---



\## 6. Day 12 — Financial Ratios Database



Created and populated:



`financial\_ratios`



Final database results:



\- Rows: 1070

\- Columns: 28

\- Duplicate company-year pairs: 0

\- Foreign-key errors: 0



Foreign-key relationship:



`financial\_ratios.company\_id -> companies.id`



5-Year CAGR availability:



\- Revenue CAGR: 612

\- PAT CAGR: 549

\- EPS CAGR: 545



\*\*Status: COMPLETE\*\*



\---



\## 7. Day 13 — Edge-Case Validation



A dedicated final validation engine was implemented.



Validation covered:



\- Table population

\- Duplicate company-year detection

\- Foreign-key integrity

\- Profitability KPI presence

\- Financial-sector leverage handling

\- High-leverage classification

\- Interest coverage classifications

\- Net Debt source limitation

\- CAGR edge-case flags

\- Insufficient CAGR history

\- CFO/PAT edge cases

\- Capex source limitation

\- Infinite KPI protection



Final validation result:



\- Checks passed: \*\*13\*\*

\- Checks failed: \*\*0\*\*

\- Overall: \*\*PASS\*\*



Output:



`output/day13\_kpi\_validation.csv`



\*\*Status: COMPLETE\*\*



\---



\## 8. Day 14 — Sprint Review and Testing



Final KPI regression suite:



\*\*51 tests passed\*\*



The test suite covers:



\- Profitability formulas

\- Zero denominators

\- Debt-to-Equity

\- Leverage classification

\- Interest Coverage

\- Debt-free handling

\- Asset Turnover

\- CAGR calculations

\- CAGR edge cases

\- CFO Margin

\- CFO/PAT

\- FCF formula behavior

\- Capex-dependent formula behavior



Final database QA:



\- financial\_ratios rows: 1070

\- duplicate company-year pairs: 0

\- foreign-key errors: 0



Edge-case documentation:



`ratio\_edge\_cases.log`



\*\*Status: COMPLETE\*\*



\---



\## 9. What Went Well



1\. Sprint 1 data was successfully reused as the analytical foundation.



2\. Financial formulas were separated into reusable functions and tested independently.



3\. The ratio engine protects against division-by-zero and invalid denominator conditions.



4\. Financial-sector leverage was handled separately instead of applying the same interpretation to all companies.



5\. CAGR calculations explicitly handle loss, turnaround, zero-base and insufficient-history situations.



6\. The final `financial\_ratios` table contains no duplicate company-year records.



7\. Foreign-key integrity passes successfully.



8\. Automated testing expanded beyond a minimal formula test set, reaching 51 passing KPI tests.



9\. Source limitations were documented rather than replacing missing financial fields with unsupported assumptions.



\---



\## 10. Challenges Encountered



\### Missing Cash Field



A dedicated cash/cash-equivalent value was unavailable, preventing reliable Net Debt calculation.



\### Missing Capex Field



A dedicated Capex value was unavailable, preventing reliable FCF, FCF Margin and Capex/Sales calculation.



\### Fiscal-Year Gaps



Some companies do not have continuous annual history.



The CAGR engine therefore matches actual fiscal-year endpoints and returns `INSUFFICIENT` where the required historical observation is absent.



\### Database Foreign Key



The `companies` table uses `id` as its primary key rather than `company\_id`.



The final ratio table was therefore correctly configured to reference:



`companies(id)`



\---



\## 11. What Could Be Improved



1\. Obtain a dedicated cash/cash-equivalent field for Net Debt.



2\. Obtain dedicated capital-expenditure data for FCF-related KPIs.



3\. Increase historical coverage to improve 10-year CAGR availability.



4\. Expand integration testing around the complete analytics pipeline.



5\. Add automated CI execution of the complete test suite on every Git push.



6\. Add richer data-quality reporting for source-vs-calculated ratio discrepancies.



\---



\## 12. Sprint Acceptance Summary



| Checkpoint | Result |

|---|---|

| Profitability engine | PASS |

| Leverage engine | PASS |

| Efficiency engine | PASS |

| CAGR engine | PASS |

| Cash-flow engine | PASS with source limitations |

| Financial-sector handling | PASS |

| financial\_ratios populated | PASS |

| Duplicate company-year rows | 0 |

| Foreign-key errors | 0 |

| KPI tests | 51 PASSED |

| Day 13 validation | 13/13 PASSED |

| Edge cases documented | PASS |



\### Source-Data Limitations



Net Debt cannot be reliably calculated because the supplied source does not contain a dedicated cash/cash-equivalent field.



FCF, FCF Margin and Capex/Sales cannot be reliably calculated because the supplied source does not contain a dedicated Capex field.



These metrics were deliberately left unavailable instead of being populated using unsupported assumptions.



\---



\## 13. Sprint Outcome



Sprint 2 successfully delivered the core Financial Ratio Engine and consolidated analytical database layer.



The final implementation contains:



\- Tested financial formulas

\- Multi-window CAGR calculations

\- Explicit edge-case classifications

\- Financial-sector-specific handling

\- Database-integrated KPI outputs

\- Automated QA validation

\- Documented source-data limitations



The final `financial\_ratios` table contains \*\*1070 unique company-year records\*\*, with \*\*0 duplicate company-year pairs\*\* and \*\*0 foreign-key integrity errors\*\*.



\*\*Sprint 2 Review Status: COMPLETE\*\*

