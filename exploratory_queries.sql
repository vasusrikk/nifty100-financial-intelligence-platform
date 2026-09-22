-- ============================================================
-- NIFTY 100 FINANCIAL INTELLIGENCE PLATFORM
-- Sprint 1 - Exploratory SQL Queries
-- ============================================================

-- Q1. Total number of companies
SELECT COUNT(*) AS total_companies
FROM companies;


-- Q2. Row count of Profit & Loss
SELECT COUNT(*) AS profit_loss_rows
FROM profitandloss;


-- Q3. Row count of Balance Sheet
SELECT COUNT(*) AS balance_sheet_rows
FROM balancesheet;


-- Q4. Row count of Cash Flow
SELECT COUNT(*) AS cash_flow_rows
FROM cashflow;


-- Q5. Number of financial years available per company in P&L
SELECT
    company_id,
    COUNT(DISTINCT year) AS years_available
FROM profitandloss
GROUP BY company_id
ORDER BY years_available DESC;


-- Q6. Companies with fewer than 5 years of P&L history
SELECT
    c.id,
    c.company_name,
    COUNT(DISTINCT p.year) AS years_available
FROM companies c
LEFT JOIN profitandloss p
    ON c.id = p.company_id
GROUP BY c.id, c.company_name
HAVING COUNT(DISTINCT p.year) < 5
ORDER BY years_available;


-- Q7. Companies with fewer than 5 years of Balance Sheet history
SELECT
    c.id,
    c.company_name,
    COUNT(DISTINCT b.year) AS years_available
FROM companies c
LEFT JOIN balancesheet b
    ON c.id = b.company_id
GROUP BY c.id, c.company_name
HAVING COUNT(DISTINCT b.year) < 5
ORDER BY years_available;


-- Q8. Companies with fewer than 5 years of Cash Flow history
SELECT
    c.id,
    c.company_name,
    COUNT(DISTINCT cf.year) AS years_available
FROM companies c
LEFT JOIN cashflow cf
    ON c.id = cf.company_id
GROUP BY c.id, c.company_name
HAVING COUNT(DISTINCT cf.year) < 5
ORDER BY years_available;


-- Q9. Check NULL values in important P&L fields
SELECT
    SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END)
        AS null_sales,
    SUM(CASE WHEN operating_profit IS NULL THEN 1 ELSE 0 END)
        AS null_operating_profit,
    SUM(CASE WHEN net_profit IS NULL THEN 1 ELSE 0 END)
        AS null_net_profit,
    SUM(CASE WHEN eps IS NULL THEN 1 ELSE 0 END)
        AS null_eps
FROM profitandloss;


-- Q10. Check NULL values in important Balance Sheet fields
SELECT
    SUM(CASE WHEN total_assets IS NULL THEN 1 ELSE 0 END)
        AS null_total_assets,
    SUM(CASE WHEN total_liabilities IS NULL THEN 1 ELSE 0 END)
        AS null_total_liabilities,
    SUM(CASE WHEN fixed_assets IS NULL THEN 1 ELSE 0 END)
        AS null_fixed_assets
FROM balancesheet;


-- Q11. Financial-year distribution in P&L
SELECT
    year,
    COUNT(*) AS records
FROM profitandloss
GROUP BY year
ORDER BY year;


-- Q12. Financial-year distribution in Balance Sheet
SELECT
    year,
    COUNT(*) AS records
FROM balancesheet
GROUP BY year
ORDER BY year;


-- Q13. Financial-year distribution in Cash Flow
SELECT
    year,
    COUNT(*) AS records
FROM cashflow
GROUP BY year
ORDER BY year;


-- Q14. Companies and their sectors
SELECT
    c.id,
    c.company_name,
    s.broad_sector,
    s.sub_sector,
    s.market_cap_category
FROM companies c
LEFT JOIN sectors s
    ON c.id = s.company_id
ORDER BY s.broad_sector, c.company_name;


-- Q15. Companies missing Balance Sheet records
SELECT
    c.id,
    c.company_name
FROM companies c
LEFT JOIN balancesheet b
    ON c.id = b.company_id
WHERE b.company_id IS NULL
ORDER BY c.id;


-- Q16. Verify orphan records in Profit & Loss
SELECT p.company_id
FROM profitandloss p
LEFT JOIN companies c
    ON p.company_id = c.id
WHERE c.id IS NULL;


-- Q17. Verify orphan records in Balance Sheet
SELECT b.company_id
FROM balancesheet b
LEFT JOIN companies c
    ON b.company_id = c.id
WHERE c.id IS NULL;


-- Q18. Verify orphan records in Cash Flow
SELECT cf.company_id
FROM cashflow cf
LEFT JOIN companies c
    ON cf.company_id = c.id
WHERE c.id IS NULL;


-- Q19. Overall time-series coverage
SELECT
    c.id,
    c.company_name,
    COUNT(DISTINCT p.year) AS pl_years,
    COUNT(DISTINCT b.year) AS bs_years,
    COUNT(DISTINCT cf.year) AS cf_years
FROM companies c
LEFT JOIN profitandloss p
    ON c.id = p.company_id
LEFT JOIN balancesheet b
    ON c.id = b.company_id
LEFT JOIN cashflow cf
    ON c.id = cf.company_id
GROUP BY c.id, c.company_name
ORDER BY c.id;


-- Q20. Database table row-count summary
SELECT 'companies' AS table_name, COUNT(*) AS rows FROM companies
UNION ALL
SELECT 'profitandloss', COUNT(*) FROM profitandloss
UNION ALL
SELECT 'balancesheet', COUNT(*) FROM balancesheet
UNION ALL
SELECT 'cashflow', COUNT(*) FROM cashflow
UNION ALL
SELECT 'analysis', COUNT(*) FROM analysis
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'prosandcons', COUNT(*) FROM prosandcons
UNION ALL
SELECT 'sectors', COUNT(*) FROM sectors
UNION ALL
SELECT 'stock_prices', COUNT(*) FROM stock_prices
UNION ALL
SELECT 'market_cap', COUNT(*) FROM market_cap
UNION ALL
SELECT 'financial_ratios', COUNT(*) FROM financial_ratios
UNION ALL
SELECT 'peer_groups', COUNT(*) FROM peer_groups;