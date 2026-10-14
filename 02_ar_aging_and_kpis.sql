-- 02_ar_aging_and_kpis.sql
-- Purpose: core project KPIs. Validate the exact financial/date definitions locally.
USE healthcare_rcm;

-- 1. Unique claims and total outstanding AR
-- Assumes Outstanding_AR is populated and represents the validated claim-level balance.
SELECT
    COUNT(DISTINCT Claim_ID) AS unique_claims,
    ROUND(SUM(CAST(Outstanding_AR AS DECIMAL(18,2))), 2) AS total_outstanding_ar
FROM fact_claims;

-- 2. Outstanding AR by aging bucket
SELECT
    AR_Aging_Bucket,
    COUNT(DISTINCT Claim_ID) AS unique_claims,
    ROUND(SUM(CAST(Outstanding_AR AS DECIMAL(18,2))), 2) AS outstanding_ar
FROM fact_claims
GROUP BY AR_Aging_Bucket
ORDER BY CASE TRIM(AR_Aging_Bucket)
    WHEN '0-30' THEN 1
    WHEN '31-60' THEN 2
    WHEN '61-90' THEN 3
    WHEN '91-120' THEN 4
    WHEN '120+' THEN 5
    ELSE 99
END;

-- 3. Denial rate based on distinct Claim_IDs in the denial table
-- This matches the project's denial-table-presence definition, not status alone.
WITH claim_count AS (
    SELECT COUNT(DISTINCT Claim_ID) AS total_claims
    FROM fact_claims
),
denied_count AS (
    SELECT COUNT(DISTINCT Claim_ID) AS claims_with_denial_record
    FROM fact_denials
)
SELECT
    c.total_claims,
    d.claims_with_denial_record,
    ROUND(100.0 * d.claims_with_denial_record / NULLIF(c.total_claims, 0), 2) AS denial_rate_pct
FROM claim_count c
CROSS JOIN denied_count d;

-- 4. AR aged 120+ days
SELECT
    COUNT(DISTINCT Claim_ID) AS claims_120_plus,
    ROUND(SUM(CAST(Outstanding_AR AS DECIMAL(18,2))), 2) AS ar_120_plus
FROM fact_claims
WHERE TRIM(AR_Aging_Bucket) = '120+';

-- 5. Reconciliation of five aging buckets to total AR
-- Compare this total with the result from query #1. Investigate any difference.
SELECT
    ROUND(SUM(CAST(Outstanding_AR AS DECIMAL(18,2))), 2) AS sum_of_aging_buckets
FROM fact_claims
WHERE TRIM(AR_Aging_Bucket) IN ('0-30', '31-60', '61-90', '91-120', '120+');

-- Note: if the source table includes duplicate Claim_ID rows, use a validated
-- cleaned claim-level table (for example fact_claims_clean) rather than blindly
-- summing duplicate rows. Confirm which table is the approved source for final KPIs.
