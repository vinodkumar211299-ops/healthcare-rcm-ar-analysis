-- 03_denial_provider_payment_analysis.sql
-- Purpose: denial-record presence, provider patterns, denial reasons, and payment coverage.
USE healthcare_rcm;

-- 1. 120+ day AR split by presence of a matching denial-table Claim_ID.
-- "No denial record" means no matching row in fact_denials; it does not prove
-- the claim was never denied.
WITH claims_clean AS (
    SELECT *
    FROM (
        SELECT
            c.*,
            ROW_NUMBER() OVER (
                PARTITION BY TRIM(c.Claim_ID)
                ORDER BY TRIM(c.Claim_ID)
            ) AS rn
        FROM fact_claims c
    ) x
    WHERE rn = 1
),
denial_ids AS (
    SELECT DISTINCT TRIM(Claim_ID) AS Claim_ID
    FROM fact_denials
    WHERE Claim_ID IS NOT NULL
)
SELECT
    CASE WHEN d.Claim_ID IS NOT NULL
         THEN 'Has denial-table match'
         ELSE 'No denial-table match'
    END AS denial_record_group,
    ROUND(SUM(CAST(c.Outstanding_AR AS DECIMAL(18,2))), 2) AS outstanding_ar
FROM claims_clean c
LEFT JOIN denial_ids d ON TRIM(c.Claim_ID) = d.Claim_ID
WHERE TRIM(c.AR_Aging_Bucket) = '120+'
GROUP BY denial_record_group;

-- 2. Denial reason counts and amounts
SELECT
    Denial_Reason_Code,
    COUNT(*) AS denial_records,
    COUNT(DISTINCT Claim_ID) AS distinct_claims,
    ROUND(SUM(CAST(Denied_Amount AS DECIMAL(18,2))), 2) AS denied_amount
FROM fact_denials
GROUP BY Denial_Reason_Code
ORDER BY denied_amount DESC;

-- 3. Provider-level claims and denial-table-presence rate.
-- First aggregate denial IDs so multiple denial rows do not multiply claim rows.
WITH claims_clean AS (
    SELECT *
    FROM (
        SELECT
            c.*,
            ROW_NUMBER() OVER (
                PARTITION BY TRIM(c.Claim_ID)
                ORDER BY TRIM(c.Claim_ID)
            ) AS rn
        FROM fact_claims c
    ) x
    WHERE rn = 1
),
denial_ids AS (
    SELECT DISTINCT TRIM(Claim_ID) AS Claim_ID
    FROM fact_denials
    WHERE Claim_ID IS NOT NULL
)
SELECT
    c.Provider_ID,
    p.Provider_Name,
    p.Specialty,
    p.Location,
    COUNT(DISTINCT c.Claim_ID) AS total_claims,
    COUNT(DISTINCT d.Claim_ID) AS claims_with_denial_record,
    ROUND(
        100.0 * COUNT(DISTINCT d.Claim_ID)
        / NULLIF(COUNT(DISTINCT c.Claim_ID), 0),
        2
    ) AS denial_record_rate_pct,
    ROUND(SUM(CAST(c.Outstanding_AR AS DECIMAL(18,2))), 2) AS total_outstanding_ar
FROM claims_clean c
LEFT JOIN dim_provider p
    ON TRIM(c.Provider_ID) = TRIM(p.Provider_ID)
LEFT JOIN denial_ids d
    ON TRIM(c.Claim_ID) = d.Claim_ID
GROUP BY c.Provider_ID, p.Provider_Name, p.Specialty, p.Location
ORDER BY denial_record_rate_pct DESC;

-- 4. Payment-record coverage by claim.
-- A matching payment row does not prove a claim was fully or partially paid.
WITH claims_clean AS (
    SELECT *
    FROM (
        SELECT
            c.*,
            ROW_NUMBER() OVER (
                PARTITION BY TRIM(c.Claim_ID)
                ORDER BY TRIM(c.Claim_ID)
            ) AS rn
        FROM fact_claims c
    ) x
    WHERE rn = 1
),
payment_ids AS (
    SELECT DISTINCT TRIM(Claim_ID) AS Claim_ID
    FROM fact_payments
    WHERE Claim_ID IS NOT NULL
)
SELECT
    CASE WHEN p.Claim_ID IS NOT NULL
         THEN 'Has payment record'
         ELSE 'No payment record'
    END AS payment_record_group,
    COUNT(DISTINCT c.Claim_ID) AS unique_claims,
    ROUND(SUM(CAST(c.Outstanding_AR AS DECIMAL(18,2))), 2) AS outstanding_ar
FROM claims_clean c
LEFT JOIN payment_ids p ON TRIM(c.Claim_ID) = p.Claim_ID
GROUP BY payment_record_group;

-- 5. Payment-record coverage within 120+ day AR with no denial-table match
WITH claims_clean AS (
    SELECT *
    FROM (
        SELECT
            c.*,
            ROW_NUMBER() OVER (
                PARTITION BY TRIM(c.Claim_ID)
                ORDER BY TRIM(c.Claim_ID)
            ) AS rn
        FROM fact_claims c
    ) x
    WHERE rn = 1
),
denial_ids AS (
    SELECT DISTINCT TRIM(Claim_ID) AS Claim_ID
    FROM fact_denials
    WHERE Claim_ID IS NOT NULL
),
payment_ids AS (
    SELECT DISTINCT TRIM(Claim_ID) AS Claim_ID
    FROM fact_payments
    WHERE Claim_ID IS NOT NULL
)
SELECT
    CASE WHEN p.Claim_ID IS NOT NULL
         THEN 'Has payment record'
         ELSE 'No payment record'
    END AS payment_record_group,
    COUNT(DISTINCT c.Claim_ID) AS unique_claims,
    ROUND(SUM(CAST(c.Outstanding_AR AS DECIMAL(18,2))), 2) AS outstanding_ar
FROM claims_clean c
LEFT JOIN denial_ids d ON TRIM(c.Claim_ID) = d.Claim_ID
LEFT JOIN payment_ids p ON TRIM(c.Claim_ID) = p.Claim_ID
WHERE TRIM(c.AR_Aging_Bucket) = '120+'
  AND d.Claim_ID IS NULL
GROUP BY payment_record_group;

-- Review provider ID formats and table columns locally before filtering for
-- Provider_0074. In the Python checkpoint, Provider_0074 was found by Provider_Name.
