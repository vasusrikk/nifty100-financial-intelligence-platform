\# Sprint 4 Retrospective



\## Sprint Objective



Sprint 4 focused on converting the NIFTY 100 analytics pipeline developed in the earlier sprints into an interactive financial analytics dashboard.



The sprint integrated company fundamentals, valuation analysis, peer comparison, screening, sector analytics, capital analysis, historical trends, annual-report access, report exports, and dashboard QA into a Streamlit-based interface.



\---



\## Major Work Completed



\### Dashboard Foundation



\- Built the Streamlit dashboard application.

\- Configured the dashboard with a wide layout and expanded sidebar.

\- Implemented reusable SQLite database-access utilities.

\- Added Streamlit caching for dashboard database queries.

\- Configured a 600-second cache TTL.



\### Home Dashboard



Implemented the market overview dashboard with:



\- Financial-period selector.

\- Average ROE.

\- Median P/E.

\- Median Debt/Equity.

\- Total Companies.

\- Median Revenue CAGR 5yr.

\- Debt-Free Companies.

\- Sector distribution visualization.

\- ROE vs Debt/Equity analysis.

\- Largest-company analysis.

\- Top 5 companies using the Sprint 3 composite quality scoring engine.



\### Company Profile



Implemented individual company analysis with:



\- Searchable company selector.

\- Company name.

\- Ticker.

\- Sector.

\- Sub-sector.

\- Market Capitalization.

\- P/E.

\- ROE.

\- ROCE.

\- Debt/Equity.

\- Revenue CAGR 5yr.

\- 10-year Revenue and Net Profit chart.

\- 10-year ROE and ROCE analysis.

\- Pros and Cons indicators.

\- Profit \& Loss table.

\- Balance Sheet table.

\- Cash Flow table.

\- Financial Ratios table.



\### Interactive Screener



Integrated the Sprint 3 screening and ranking engine into the dashboard.



The screener supports fundamental metrics including:



\- ROE.

\- ROCE.

\- Debt/Equity.

\- Interest Coverage Ratio.

\- Revenue CAGR.

\- PAT CAGR.

\- CFO Margin.

\- CFO/PAT.

\- FCF Margin.

\- P/E.

\- Dividend Yield.



The existing financial-sector Debt/Equity handling and debt-free Interest Coverage Ratio logic were retained.



Screener results support:



\- Matching-company count.

\- Composite quality scoring.

\- Ranking.

\- Result table.

\- CSV export.



\### Peer Comparison



Completed peer analytics using the supplied peer-group source.



Final peer-group source statistics:



\- 56 companies.

\- 11 peer groups.

\- 840 peer-percentile records.

\- 12-sheet peer-comparison workbook.



Peer radar-chart generation was completed for all 56 expected peer companies.



The M\&M filename normalization issue was corrected so the final radar set contains:



\- Expected: 56

\- Generated: 56

\- Missing: 0

\- Extra: 0



\### Valuation Analysis



Completed sector-relative valuation analysis for 92 companies.



Valuation coverage:



\- P/E populated: 92 companies.

\- P/B populated: 92 companies.

\- EV/EBITDA populated: 92 companies.

\- FCF Yield populated: 0 companies because the source data does not contain populated FCF values for the required valuation period.



Valuation classifications were generated using:



\- Discount.

\- In Line.

\- Caution.



Generated:



`reports/valuation\_summary.xlsx`



Also generated:



`output/valuation\_flags.csv`



The valuation-flags export contains 75 companies having at least one Discount or Caution valuation flag.



No FCF or FCF Yield values were fabricated where source data was unavailable.



\### Annual Reports



Integrated annual-report browsing using the SQLite `documents` table.



Document dataset:



\- 1,457 document records.

\- 91 companies with annual-report records.



DIVISLAB was identified as the company without an annual-report record in the available dataset.



Annual-report handling includes:



\- Company selection.

\- Financial-year selection.

\- BSE annual-report links.

\- Missing-record handling.

\- Missing-link handling.

\- HTTP URL availability checking.

\- 404 handling.

\- Timeout handling.

\- Unreachable-link handling.

\- Cached URL availability checks.



Unavailable annual reports are displayed as unavailable instead of being represented as working links.



\### Reports \& Export Center



Completed the reports and export interface for:



\- Peer Comparison workbook.

\- Screener workbook.

\- Valuation Summary workbook.

\- Custom Screen CSV.

\- Custom Screen JSON.

\- Company radar-chart PNG files.

\- Generated-file inventory.



The report inventory includes the valuation workbook in the total generated-report count.



\### Dashboard QA



Dashboard QA documentation was maintained in:



`dashboard\_qa.md`



QA work included:



\- Representative ticker checks.

\- Missing-data handling.

\- Peer-data checks.

\- Radar-chart completeness.

\- Annual-report edge cases.

\- Dashboard caching checks.

\- Profile data-load performance testing.



Five representative company profiles were performance tested:



| Ticker | Load Time |

|---|---:|

| TCS | 0.018 sec |

| ONGC | 0.007 sec |

| SUNPHARMA | 0.010 sec |

| BAJFINANCE | 0.010 sec |

| ADANIGREEN | 0.008 sec |



All five completed their tested data-loading operations well below the 3-second requirement.



\---



\## Key Issues Resolved



During Sprint 4, the following issues were identified and addressed:



1\. Missing peer-percentile coverage was investigated against the actual peer-group source.

2\. The project was confirmed to contain 56 source peer companies across 11 peer groups.

3\. Radar-chart ticker normalization for M\&M was corrected.

4\. Valuation Summary was added to the Reports \& Export Center.

5\. The generated-report inventory was updated to include the valuation workbook.

6\. Annual-report missing-data and dead-link handling was strengthened.

7\. FCF Yield unavailability was documented rather than estimated from incomplete data.

8\. Dashboard database access uses caching to improve repeated-query performance.

9\. Profile data-loading performance was measured using representative companies.

10\. The missing `output/valuation\_flags.csv` artifact was generated.



\---



\## Sprint Deliverables



Important Sprint 4 outputs include:



\- Streamlit analytics dashboard.

\- `reports/peer\_comparison.xlsx`

\- `reports/screener\_output.xlsx`

\- `reports/valuation\_summary.xlsx`

\- `reports/radar\_charts/`

\- `output/valuation\_flags.csv`

\- `dashboard\_qa.md`

\- `sprint4\_retro.md`



\---



\## Sprint 4 Final Status



\*\*Sprint 4 implementation activities completed.\*\*



The project now provides an integrated dashboard layer over the previously developed NIFTY 100 data, analytics, screening, peer-comparison and valuation pipelines while explicitly representing missing source data rather than fabricating unavailable financial information.

