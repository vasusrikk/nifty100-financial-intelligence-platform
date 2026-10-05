# Nifty 100 Financial Intelligence Platform

## Day 43 - Integration and Performance Test Notes



### Test Date

02 October 2026



### Environment

* Application: Nifty 100 Financial Intelligence Platform
* API Framework: FastAPI
* API Server: Uvicorn
* API Address: http://127.0.0.1:8000
* Dashboard Framework: Streamlit
* Database: SQLite
* Database File: nifty100.db



## 1\. API-Dashboard Data Consistency Test



The FastAPI service and Streamlit dashboard data layer were tested against the

same Nifty 100 platform data.



Results:



* API company count: 92
* Dashboard company count: 92
* API TCS company name: Tata Consultancy Services Ltd
* Dashboard TCS company name: Tata Consultancy Services Ltd
* Data consistency status: PASS



The API and dashboard returned consistent company-universe information for the

tested records.



## 2\. Concurrent API Load Test



Endpoint tested:



GET /api/analytics/latest-ratios?limit=20



Test configuration:



* Total requests: 10
* Concurrent workers: 10
* Request timeout: 15 seconds



Measured results:



* Successful requests: 10 / 10
* HTTP status codes: 200 for all requests
* Minimum response time: 37.56 ms
* Average response time: 53.94 ms
* Maximum response time: 75.83 ms
* Total wall-clock time: 77.88 ms
* Failed requests: 0



Load test status: PASS



## 3\. Observations



All ten concurrent API requests completed successfully.



No HTTP errors, request timeouts, or API crashes were observed during the test.



The tested API endpoint remained responsive under the required 10-request

concurrent workload.



No performance bottleneck requiring corrective action was identified during

this test.



## 4\. Day 43 Result



API/dashboard consistency: PASS



10-concurrent-request load test: PASS



Overall Day 43 integration testing status: PASS

