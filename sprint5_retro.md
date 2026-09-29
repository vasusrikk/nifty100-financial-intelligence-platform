\# Sprint 5 Retrospective - Intelligence \& Reports



\## Sprint Objective



Sprint 5 completed the intelligence and automated reporting layer of the NIFTY100 Financial Intelligence Platform.



The sprint covered financial-text parsing, explainable Pros and Cons generation, cash-flow intelligence, capital-allocation analysis, automated two-page PDF tear sheets, batch PDF generation, final QA, and project documentation.



\---



\## Day 29 - Analysis Parser



Implemented a structured parser for financial text contained in the Analysis dataset.



\### Completed



\- Parsed financial growth text into structured values

\- Extracted periods and percentage values

\- Processed Sales Growth

\- Processed Profit Growth

\- Processed Stock Price CAGR

\- Processed ROE

\- Added CAGR validation against the analytics engine

\- Added manual-review handling for material divergence



\### Final Results



\- Parsed rows: 80

\- Companies: 5

\- Parse failures: 0

\- CAGR validations: 30

\- Validation pass: 23

\- Manual review: 1

\- Not comparable: 6



\### Output



`output/analysis\_parsed.csv`



\---



\## Day 30 - Pros and Cons Intelligence



Implemented an explainable rule-based financial signal generator.



\### Completed



\- 12 PRO rules

\- 12 CON rules

\- Financial metric-based signal generation

\- Human-readable signal messages

\- Separate storage of generated intelligence

\- Original Pros and Cons source data preserved



\### Final Results



\- Total signals: 80

\- PRO signals: 71

\- CON signals: 9

\- Companies represented: 5



\### Outputs



`output/pros\_cons.csv`



Database table:



`generated\_pros\_cons`



\---



\## Day 31 - Cash Flow Intelligence



Implemented company-level CFO quality scoring and financial-distress pattern analysis.



\### CFO Quality



Quality classes:



\- STRONG

\- GOOD

\- MODERATE

\- WEAK



Final results:



\- Companies: 91

\- Rows: 91

\- Minimum score: 0

\- Maximum score: 100

\- STRONG: 68

\- GOOD: 7

\- MODERATE: 4

\- WEAK: 12



Output:



`output/cfo\_quality\_score.csv`



\### Distress Pattern Analysis



Implemented detection for:



\- Repeated negative CFO

\- Persistent CFO below PAT

\- Declining CFO trend

\- Negative latest CFO

\- Financing dependence



Final distress distribution:



\- NONE: 49

\- LOW: 22

\- MODERATE: 4

\- HIGH: 16



Output:



`output/cashflow\_distress\_flags.csv`



\---



\## Day 32 - Capital Allocation Intelligence



Implemented a company-level capital-allocation matrix using available cash-flow evidence.



\### Allocation Classes



\- INTERNALLY\_FUNDED\_INVESTMENT

\- EXTERNALLY\_FUNDED\_INVESTMENT

\- CASH\_ACCUMULATION

\- INVESTING\_INFLOW

\- FINANCING\_DEPENDENT

\- MIXED



\### Final Results



\- Companies: 91

\- Rows: 91



CapEx intensity:



\- Available: 0

\- Unavailable: 91

\- Status: CAPEX\_SOURCE\_UNAVAILABLE



No CapEx value was fabricated from investing cash flow.



\### Outputs



`output/capital\_allocation\_matrix.csv`



`output/cashflow\_intelligence.xlsx`



The workbook contains four sheets:



1\. Company Summary

2\. CFO Quality

3\. Distress Flags

4\. Capital Allocation



\---



\## Day 33 - PDF Tearsheet Template



Implemented a professional two-page company financial tear sheet using ReportLab and Matplotlib.



\### Page 1



\- Company/ticker header

\- Six KPI tiles

\- Revenue chart

\- Net Profit chart

\- ROE/ROCE trend chart



\### Page 2



\- Balance Sheet composition

\- Cash Flow analysis

\- Generated Pros

\- Generated Cons

\- Capital Allocation classification



\### Cross-Sector Testing



Tested:



\- TCS

\- HDFCBANK

\- RELIANCE

\- SUNPHARMA

\- TATASTEEL



Final results:



\- Generated: 5

\- Failed: 0

\- Correct two-page PDFs: 5



Main module:



`src/reports/tearsheet.py`



\---



\## Day 34 - Batch PDF Generation



Extended the PDF engine to the complete company universe.



\### Completed



\- Batch company iteration

\- One PDF per company

\- PDF existence validation

\- PDF readability validation

\- File-size validation

\- Two-page validation

\- Failure logging

\- Validation CSV generation



\### Final Results



\- Total companies: 92

\- Generation pass: 92

\- Generation failures: 0

\- Validation pass: 92

\- Correct two-page PDFs: 92

\- Failures: 0



\### Outputs



`reports/tearsheets/`



`output/day34\_pdf\_validation.csv`



`logs/pdf\_failures.log`



Main module:



`src/reports/batch\_generate.py`



\---



\## Day 35 - Final QA \& Documentation



Final PDF QA confirmed:



\- Total companies: 92

\- Generation pass: 92

\- Validation pass: 92

\- Two-page pass: 92

\- Failures: 0



The project README was expanded to document the complete Sprint 1 through Sprint 5 platform.



Documentation includes:



\- Project overview

\- Sprint implementation history

\- Platform architecture

\- Analytics and intelligence components

\- Reporting system

\- Known limitations

\- Data-integrity principles

\- Educational-use disclaimer



\---



\## What Went Well



\- Sprint 5 completed the intelligence layer without replacing the validated financial-data foundation.

\- Financial-text parsing achieved zero parse failures for the processed Analysis records.

\- Generated Pros and Cons remained separate from original source commentary.

\- Cash-flow quality and distress analytics produced company-level explainable classifications.

\- Missing CapEx data was handled explicitly instead of being fabricated.

\- The PDF reporting engine successfully handled companies across different sectors.

\- Batch PDF generation achieved 92 out of 92 successful reports.

\- All 92 final PDFs passed the required two-page validation.

\- Automated failure logging and validation outputs improved auditability.



\---



\## Challenges Encountered



\- Analysis source coverage was limited compared with the complete company universe.

\- Financial edge cases required explicit handling instead of generic calculations.

\- The source database did not contain a reliable explicit CapEx field.

\- Generated Pros and Cons required handling companies that had only PRO or only CON signals.

\- PDF layouts had to support variable company data without creating unexpected additional pages.

\- Batch report generation required validation so that successful file creation alone was not treated as sufficient QA.



\---



\## Key Decisions



1\. Preserve original source financial information.

2\. Keep generated intelligence separate from original commentary.

3\. Do not treat investing cash flow as CapEx.

4\. Mark unavailable financial metrics explicitly.

5\. Use explainable rules for financial Pros and Cons.

6\. Validate every generated PDF automatically.

7\. Require exactly two pages for each final company tear sheet.

8\. Log report-generation and validation failures.



\---



\## Known Limitations



\- Explicit CapEx data is unavailable in the supplied source database.

\- Some CapEx-dependent KPIs therefore remain unavailable.

\- Analysis workbook coverage is smaller than the complete 92-company universe.

\- Historical financial coverage varies by company.

\- Generated Pros and Cons are rule-based analytical signals.

\- Tear sheets use locally available project data rather than automatically retrieving live market information.



\---



\## Sprint 5 Final Outcome



Sprint 5 successfully transformed the project from a financial analytics platform into an intelligence and automated reporting system.



The final platform now integrates:



Raw Data -> ETL -> SQLite -> Financial Analytics -> Peer/Valuation Analytics -> NLP Intelligence -> Cash Flow Intelligence -> Capital Allocation -> Dashboard -> Automated PDF Reports



Final PDF reporting result:



\*\*92 companies processed, 92 PDFs generated, 92 PDFs validated, 0 failures.\*\*



\---



\## Disclaimer



\*\*For educational purposes only. Not investment advice.\*\*

