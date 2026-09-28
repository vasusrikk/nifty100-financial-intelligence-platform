\# Sprint 4 Dashboard QA Report



\## Project

NIFTY 100 Financial Intelligence Platform



\## QA Scope

Sprint 4 - Day 27 Dashboard Integration Testing



\## Test Universe

Total companies in platform: 92



Random QA sample:

\- SUNPHARMA

\- BAJFINANCE

\- ADANIGREEN

\- HAL

\- EICHERMOT

\- DLF

\- BHARTIARTL

\- BAJAJHLDNG

\- TCS

\- ONGC



\## Screen Test Results



| Screen | Result | Notes |

|---|---|---|

| Home | PASS | Summary KPIs, coverage, sector distribution and rankings rendered correctly |

| Company Profile | PASS | 10/10 sampled companies tested successfully |

| Screener | PASS | Full universe, filtering, reset, result table and CSV export verified |

| Peer Comparison | PASS | Peer comparisons render correctly; missing peer data handled safely |

| Trend Analysis | PASS | 10/10 sampled companies tested; stock and financial trends rendered |

| Sector Analysis | PASS | All 10 available broad sectors tested successfully |

| Capital | PASS | 10/10 sampled companies tested; missing FCF/CapEx data handled safely |

| Reports / Annual Reports | PASS | 61 generated files recognized; downloads and annual-report browser verified |



\## Missing-Data / Edge-Case Tests



\### Peer Data

The supplied peer\_groups.xlsx contains 56 company assignments across 11 peer groups.



Peer radar coverage:

\- Expected from supplied source: 56

\- Generated: 56

\- Missing: 0

\- Extra: 0



Companies without supplied peer assignments are handled safely by the dashboard rather than receiving fabricated peer memberships.



\### Annual Reports

The documents table contains:

\- 1,457 records

\- 91 companies



DIVISLAB has no annual-report record and was tested as the missing-report case.



Result:

PASS - the dashboard displays an Annual Report Unavailable message without crashing.



\### Valuation / FCF

The 2024-03 valuation dataset provides complete P/E, P/B and EV/EBITDA coverage for all 92 companies.



Source FCF coverage is zero for the selected valuation year. FCF Yield therefore remains unavailable rather than being derived from incomplete source data.



Result:

PASS - missing source data is represented explicitly.



\## Valuation Verification



Valuation summary:

\- Companies: 92

\- P/E populated: 92

\- P/B populated: 92

\- EV/EBITDA populated: 92



P/E flags:

\- In Line: 48

\- Discount: 30

\- Caution: 14



P/B flags:

\- In Line: 45

\- Discount: 27

\- Caution: 20



EV/EBITDA flags:

\- In Line: 62

\- Discount: 24

\- Caution: 6



\## Reports Verification



\- Excel Reports: 3

\- Custom Exports: 2

\- Radar Charts: 56

\- Total Report Files: 61



Valuation Summary, Peer Comparison and Screener workbooks are available through the dashboard.



\## Final QA Result



PASS



All 8 Streamlit dashboard screens were navigated and tested successfully.



No critical dashboard errors were observed during the Day 27 integration QA.



Missing-data cases for peer assignments, annual reports and FCF-related valuation data are handled without application failure.













\---



\## Day 27 - Final Dashboard QA Update



\### Company Profile Performance Test



The Company Profile data-loading pipeline was tested using five representative companies.



| Ticker | Load Time | Requirement | Result |

|---|---:|---:|---|

| TCS | 0.018 sec | Under 3 sec | PASS |

| ONGC | 0.007 sec | Under 3 sec | PASS |

| SUNPHARMA | 0.010 sec | Under 3 sec | PASS |

| BAJFINANCE | 0.010 sec | Under 3 sec | PASS |

| ADANIGREEN | 0.008 sec | Under 3 sec | PASS |



All tested company-profile data loads completed well below the 3-second performance requirement.



\### Additional QA Fixes Completed



\- Annual-report records are loaded from the SQLite documents table.

\- Missing annual-report records are handled without crashing the dashboard.

\- Missing annual-report links are displayed as unavailable.

\- Annual-report URLs are checked for HTTP availability before being presented as usable.

\- Dead, 404, timeout, and unreachable annual-report URLs are displayed as unavailable.

\- URL availability checks are cached to avoid unnecessary repeated network requests.

\- Valuation flags export created at `output/valuation\_flags.csv`.

\- Valuation flags export contains 75 companies identified by the completed valuation flagging process.

\- Dashboard database queries use Streamlit caching with a 600-second TTL.

\- Missing financial values continue to be displayed as unavailable rather than being fabricated.



\### Day 27 Status



\*\*PASS - Dashboard QA and performance testing completed.\*\*

