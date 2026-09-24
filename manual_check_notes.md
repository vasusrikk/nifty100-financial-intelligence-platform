\# Sprint 1 - Manual Data Quality Check Notes



\## Objective



Manually verify five representative companies across Profit \& Loss,

Balance Sheet, and Cash Flow data as required by Sprint 1 Day 06.



Companies reviewed:



\- TCS

\- RELIANCE

\- HDFCBANK

\- INFY

\- ICICIBANK



Three recent annual periods were reviewed for each company.



\---



\## 1. TCS



\### Profit \& Loss



| Year | Sales | Net Profit |

|---|---:|---:|

| 2024-03 | 240893 | 46099 |

| 2023-03 | 225458 | 42303 |

| 2022-03 | 191754 | 38449 |



\### Balance Sheet



| Year | Total Assets | Total Liabilities |

|---|---:|---:|

| 2024-09 | 161124 | 161124 |

| 2024-03 | 145472 | 145472 |

| 2023-03 | 142859 | 142859 |



\### Cash Flow



| Year | Operating Activity | Net Cash Flow |

|---|---:|---:|

| 2024-03 | 44338 | 1893 |

| 2023-03 | 41965 | -5365 |

| 2022-03 | 39949 | 5630 |



\*\*Observation:\*\* Data is populated across all three statements.

Balance Sheet contains an additional 2024-09 period.



\---



\## 2. RELIANCE



\### Profit \& Loss



| Year | Sales | Net Profit |

|---|---:|---:|

| 2024-03 | 899041 | 79020 |

| 2023-03 | 876396 | 74088 |

| 2022-03 | 694673 | 67845 |



\### Balance Sheet



| Year | Total Assets | Total Liabilities |

|---|---:|---:|

| 2024-09 | 1815123 | 1815123 |

| 2024-03 | 1755048 | 1755048 |

| 2023-03 | 1605882 | 1605882 |



\### Cash Flow



| Year | Operating Activity | Net Cash Flow |

|---|---:|---:|

| 2024-03 | 158788 | 28561 |

| 2023-03 | 115032 | 32486 |

| 2022-03 | 110654 | 18781 |



\*\*Observation:\*\* Data is populated across all three statements.

Balance Sheet contains an additional 2024-09 period.



\---



\## 3. HDFCBANK



\### Profit \& Loss



| Year | Sales | Net Profit |

|---|---:|---:|

| 2024-03 | 283649 | 65446 |

| 2023-03 | 170754 | 46149 |

| 2022-03 | 135936 | 38151 |



\### Balance Sheet



| Year | Total Assets | Total Liabilities |

|---|---:|---:|

| 2024-03 | 4030194 | 4030194 |

| 2023-03 | 2530432 | 2530432 |

| 2022-03 | 2122934 | 2122934 |



\### Cash Flow



| Year | Operating Activity | Net Cash Flow |

|---|---:|---:|

| 2024-03 | 19069 | 31687 |

| 2023-03 | 20814 | 41762 |

| 2022-03 | -11960 | 34113 |



\*\*Observation:\*\* Three annual periods are available across all three

financial statements. Negative operating cash flow in 2022-03 is

retained as reported data and is not automatically treated as an ETL error.



\---



\## 4. INFY



\### Profit \& Loss



| Year | Sales | Net Profit |

|---|---:|---:|

| 2024-03 | 153670 | 26248 |

| 2023-03 | 146767 | 24108 |

| 2022-03 | 121641 | 22146 |



\### Balance Sheet



| Year | Total Assets | Total Liabilities |

|---|---:|---:|

| 2024-09 | 141870 | 141870 |

| 2024-03 | 136020 | 136020 |

| 2023-03 | 124596 | 124596 |



\### Cash Flow



| Year | Operating Activity | Net Cash Flow |

|---|---:|---:|

| 2024-03 | 25210 | 2613 |

| 2023-03 | 22467 | -5299 |

| 2022-03 | 23885 | -7242 |



\*\*Observation:\*\* Data is populated across all three statements.

Balance Sheet contains an additional 2024-09 period. Negative net

cash-flow values are preserved as valid source observations.



\---



\## 5. ICICIBANK



\### Profit \& Loss



| Year | Sales | Net Profit |

|---|---:|---:|

| 2024-03 | 159516 | 46081 |

| 2023-03 | 121067 | 35461 |

| 2022-03 | 95407 | 26538 |



\### Balance Sheet



| Year | Total Assets | Total Liabilities |

|---|---:|---:|

| 2024-03 | 2364063 | 2364063 |

| 2023-03 | 1958490 | 1958490 |

| 2022-03 | 1752637 | 1752637 |



\### Cash Flow



| Year | Operating Activity | Net Cash Flow |

|---|---:|---:|

| 2024-03 | 157284 | 26312 |

| 2023-03 | -3771 | -46669 |

| 2022-03 | 58111 | 36114 |



\*\*Observation:\*\* Three annual periods are available across all three

statements. Negative cash-flow observations are retained as reported

financial data.



\---



\## Manual Review Summary



All five Sprint 1 Day 06 companies were successfully located and

reviewed across Profit \& Loss, Balance Sheet, and Cash Flow.



Database coverage:



| Company | P\&L Rows | Balance Sheet Rows | Cash Flow Rows |

|---|---:|---:|---:|

| TCS | 12 | 13 | 12 |

| RELIANCE | 12 | 13 | 12 |

| HDFCBANK | 12 | 12 | 12 |

| INFY | 12 | 13 | 12 |

| ICICIBANK | 12 | 12 | 12 |



\### Noted Items



1\. TCS, RELIANCE, and INFY contain a 2024-09 Balance Sheet observation

&#x20;  in addition to annual March observations.

2\. Negative cash-flow values occur in some periods and are preserved

&#x20;  because negative cash flow is not by itself evidence of an ETL defect.

3\. No missing statement was identified for the five required companies

&#x20;  during this database coverage review.

4\. The manual review did not modify or fabricate source financial values.



\## Day 06 Status



Manual five-company database spot-check completed.

