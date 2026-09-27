\# Sprint 3 Retrospective



\## Project

NIFTY 100 Financial Intelligence Platform



\## Sprint

Sprint 3 — Screening, Ranking, Peer Analytics and Reporting



\## Sprint Status

\*\*COMPLETED\*\*



\---



\# 1. Sprint Objective



The objective of Sprint 3 was to transform the financial KPI dataset developed in the earlier sprints into an analytical decision-support layer.



The sprint focused on:



\- Financial stock screening

\- Preset investment screeners

\- Company scoring and ranking

\- Sector-based analysis

\- Excel reporting

\- Peer-group modelling

\- Peer percentile analytics

\- Radar-chart visualisation

\- Peer comparison reporting

\- Final data-quality validation



The sprint was designed to build analytical functionality on top of the existing financial database without fabricating unavailable financial information.



\---



\# 2. Sprint Deliverables



\## Day 15 — Screener Foundation



Implemented the core screening infrastructure for the NIFTY 100 financial universe.



The screener layer provides structured access to company financial KPIs and supports filtering companies using quantitative financial conditions.



Key outcome:



\- Financial universe successfully loaded into the screener

\- Reusable screening architecture established

\- Financial metrics made available for downstream screening and ranking



\---



\## Day 16 — Preset Screeners



Implemented predefined financial screening strategies.



Preset screeners include:



1\. Quality Compounder

2\. Value Pick

3\. Growth Accelerator

4\. Dividend Champion

5\. Debt-Free Blue Chip

6\. Turnaround Watch



The implementation distinguishes between fully evaluable presets and presets affected by unavailable source fields.



A major identified limitation was the absence of an explicit Capex source required for complete Free Cash Flow evaluation.



No artificial Capex or FCF values were introduced.



\---



\## Day 17 — Scoring, Ranking and Sector Analysis



Implemented company scoring and ranking functionality.



The scoring engine uses multiple financial dimensions including:



\- ROE

\- ROCE

\- Net Profit Margin

\- Revenue CAGR

\- PAT CAGR

\- Debt / Equity

\- Interest Coverage Ratio

\- CFO Margin



\### Scoring safeguards



The scoring system includes:



\- Winsorisation of extreme financial values

\- 0–100 normalization

\- Weighted composite scoring

\- Missing-value-aware weight normalization

\- Deterministic ranking

\- Score coverage reporting



Extreme values are controlled during scoring without modifying raw database values.



\### Sector Ranking



Implemented sector-level ranking using the required category weighting:



\- Profitability — 50%

\- Growth — 30%

\- Valuation — 20%



Verified financial universe:



\- Companies: 92

\- Broad sectors: 10



Broad sectors:



\- Communication Services

\- Consumer Discretionary

\- Consumer Staples

\- Energy

\- Financials

\- Healthcare

\- Industrials

\- Information Technology

\- Materials

\- Real Estate



\### Excel Screener Output



Generated:



`reports/screener\_output.xlsx`



Workbook contains seven sheets:



1\. Ranked Universe

2\. Quality Compounder

3\. Value Pick

4\. Growth Accelerator

5\. Dividend Champion

6\. Debt-Free Blue Chip

7\. Turnaround Watch



\---



\# 3. Day 18 — Peer Group and Percentile Analytics



Implemented peer-group financial comparison.



The supplied peer-group dataset contained:



\- 11 peer groups

\- 56 company memberships

\- 1 benchmark company per peer group



Peer groups:



1\. Private Banks

2\. Public Sector Banks

3\. IT Services

4\. Pharmaceuticals

5\. Automobiles

6\. Life Insurance

7\. Oil \& Gas

8\. Power \& Utilities

9\. Steel

10\. FMCG

11\. Consumer Finance



\### Benchmark Companies



| Peer Group | Benchmark |

|---|---|

| Private Banks | HDFCBANK |

| Public Sector Banks | SBIN |

| IT Services | TCS |

| Pharmaceuticals | SUNPHARMA |

| Automobiles | MARUTI |

| Life Insurance | LICI |

| Oil \& Gas | RELIANCE |

| Power \& Utilities | NTPC |

| Steel | TATASTEEL |

| FMCG | HINDUNILVR |

| Consumer Finance | BAJFINANCE |



\### Peer Percentile Engine



Financial peer percentiles were calculated across 15 metrics.



Verified results:



\- Peer groups: 11

\- Memberships: 56

\- Metrics: 15

\- Expected percentile records: 840

\- Stored percentile records: 840

\- Populated percentiles: 818

\- Missing percentiles: 22



The missing percentile values remain NULL where the required source metric is unavailable.



No missing financial values were fabricated.



\---



\# 4. Day 19 — Peer Radar Charts



Implemented peer-percentile radar-chart generation using Matplotlib.



Radar charts compare individual company percentile performance against the corresponding peer-group median.



Six radar dimensions are used:



\- ROE

\- ROCE

\- Revenue Growth

\- PAT Growth

\- CFO Margin

\- P/E Value



Verified output:



\- Peer groups represented: 11

\- Peer-group companies: 56

\- Radar metrics: 6

\- PNG charts generated: 56

\- PNG files verified: 56

\- Missing radar percentile values: 10



Charts are generated only for companies explicitly assigned to the supplied peer groups.



The remaining companies in the broader 92-company universe are not assigned artificial peer groups.



Generated charts are stored under:



`reports/radar\_charts/`



\---



\# 5. Day 20 — Peer Comparison Excel



Implemented the peer comparison Excel reporting engine.



Generated:



`reports/peer\_comparison.xlsx`



Verified workbook:



\- Peer groups: 11

\- Companies: 56

\- Financial metrics: 15

\- Worksheets: 12



Workbook structure:



\- 1 Peer Group Summary sheet

\- 11 individual peer-group sheets



Each peer-group worksheet contains:



\- Company ID

\- Company name

\- Benchmark indicator

\- Financial year

\- Raw financial metric values

\- Corresponding peer percentiles



The benchmark company is positioned first within each peer-group comparison.



The report generation process is read-only with respect to source financial information.



\---



\# 6. Day 21 — Final Data Quality Audit



Implemented a dedicated Sprint 3 final audit module:



`src/analytics/sprint3\_audit.py`



The audit validates the complete analytical pipeline.



\### Final Audit Result



\*\*STATUS: PASS\*\*



\- Total audit checks: 23

\- Passed: 23

\- Failed: 0



Verified items include:



\- Companies table exists

\- Sectors table exists

\- Peer percentile table exists

\- 92-company universe

\- No duplicate company IDs

\- 10 broad sectors

\- 8 scoring metrics

\- Scoring weights total 1.0

\- Positive scoring weights

\- 840 peer percentile rows

\- 11 peer groups

\- 56 peer memberships

\- 15 peer metrics

\- Correct peer metric configuration

\- 15 metrics per peer membership

\- 11 benchmark companies

\- Exactly one benchmark per peer group

\- Percentiles constrained to 0–100

\- 818 populated percentile values

\- 22 legitimate missing percentile values

\- Missing source values were not fabricated

\- 6 radar metrics

\- Unique radar dimensions



\---



\# 7. Automated Testing



Sprint 3 introduced extensive automated validation for the analytical components.



Major test areas include:



\- Screener engine

\- Preset screeners

\- Scoring and ranking

\- Sector ranking

\- Peer analytics

\- Peer percentile calculations

\- Radar chart generation

\- Excel report generation

\- Database integrity

\- Final Sprint 3 audit



\### Final Full Regression Result



\*\*413 tests passed\*\*



No regression failures remained at Sprint completion.



\---



\# 8. Data Quality Principles Followed



Sprint 3 followed several important financial-data quality rules.



\### Raw data preservation



Winsorisation and normalization are applied only during analytical calculations.



Raw financial values stored in the database are not overwritten.



\### Missing-value preservation



Unavailable source metrics remain NULL rather than being automatically converted to zero.



\### No fabricated peer membership



Only the 56 companies explicitly present in the supplied peer-group source are included in peer-percentile analytics.



\### Deterministic ranking



Company ranking includes deterministic tie-breaking to ensure reproducible results.



\### Source limitation transparency



Analytical features affected by unavailable source information are explicitly identified rather than silently approximated.



\---



\# 9. Known Source Limitations



Three important source limitations remain documented.



\## 1. Missing Peer Metrics



22 peer percentile records remain NULL because the corresponding source financial values are unavailable.



\## 2. Peer Group Coverage



The financial universe contains 92 companies.



The supplied peer-group source explicitly defines peer membership for 56 companies across 11 groups.



Therefore, peer analytics are restricted to those 56 companies.



The remaining companies are not assigned fabricated peer groups.



\## 3. Free Cash Flow / Capex



Some preset screener rules require Free Cash Flow evaluation.



Explicit Capex source data is unavailable in the current dataset.



Therefore, presets dependent on this condition are marked as source-limited rather than using estimated or fabricated Capex values.



\---



\# 10. Technical Components Added



Important Sprint 3 components include:



`src/screener/`



\- engine.py

\- presets.py

\- scoring.py

\- custom\_screener.py

\- comparison.py

\- exporter.py



`src/analytics/`



\- peer.py

\- radar.py

\- peer\_comparison.py

\- sprint3\_audit.py



`tests/analytics/`



\- Peer analytics tests

\- Radar-chart tests

\- Peer-comparison tests

\- Sprint 3 audit tests



Generated analytical reports are stored under:



`reports/`



and are intentionally excluded from source-control tracking where appropriate.



\---



\# 11. What Went Well



Sprint 3 successfully converted the project's financial dataset into a reusable analytics layer.



Major strengths were:



\- Modular screener architecture

\- Reusable financial ranking engine

\- Robust handling of extreme values

\- Transparent missing-data handling

\- Sector-level financial analysis

\- Structured peer-group analytics

\- Percentile-based company comparison

\- Automated visual reporting

\- Excel-based analytical outputs

\- Strong automated test coverage

\- Dedicated final data-quality audit



The analytical pipeline was validated without compromising source-data integrity.



\---



\# 12. Challenges Encountered



Several implementation challenges were identified during the sprint.



\### Extreme financial ratios



Some companies contained unusually large financial ratios.



This required winsorisation before normalization so that extreme observations did not dominate company scores.



\### Missing source metrics



Not every company had every required financial metric.



The scoring system therefore required missing-value-aware weighting.



\### Peer coverage mismatch



The overall universe contained 92 companies while the supplied peer dataset covered only 56.



The implementation preserved this distinction rather than creating unsupported peer assignments.



\### SQLite file changes during tests



Some tests rebuilding derived tables caused the SQLite database file to appear modified in Git even when the logical data remained equivalent.



The committed database state was restored after regression testing where appropriate.



\### Excel and chart reporting



Reporting required additional validation to ensure generated workbooks and PNG files were structurally valid and non-empty.



\---



\# 13. Lessons Learned



Sprint 3 demonstrated that financial analytics require more than simply calculating ratios.



Reliable analytical systems must also handle:



\- Outliers

\- Missing data

\- Peer comparability

\- Source limitations

\- Deterministic calculations

\- Reproducible outputs

\- Data lineage

\- Automated validation



Separating raw financial data from derived analytical calculations significantly improves reliability and auditability.



\---



\# 14. Sprint 3 Final Validation Summary



| Validation Item | Result |

|---|---:|

| Company Universe | 92 |

| Broad Sectors | 10 |

| Peer Groups | 11 |

| Peer Memberships | 56 |

| Peer Metrics | 15 |

| Peer Percentile Rows | 840 |

| Populated Percentiles | 818 |

| Missing Percentiles | 22 |

| Benchmark Companies | 11 |

| Radar Metrics | 6 |

| Radar Charts | 56 |

| Peer Comparison Sheets | 12 |

| Final Audit Checks | 23 / 23 PASS |

| Full Regression Tests | 413 PASS |



\---



\# 15. Sprint Outcome



\## SPRINT 3 — SUCCESSFULLY COMPLETED



Sprint 3 delivered the screening, ranking, sector analysis, peer analytics, visualization, Excel reporting, and final data-quality validation layers required for the NIFTY 100 Financial Intelligence Platform.



The project now has a tested analytical foundation that can support the next sprint's higher-level platform functionality.

