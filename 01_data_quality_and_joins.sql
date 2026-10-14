-- 01_data_quality_and_joins.sql
-- Purpose: basic row/key checks and examples of safe joins.
-- Review actual column names/types in your local schema before running.

USE healthcare_rcm;

-- 1. Row counts for the seven source tables
SELECT 'dim_patient' AS table_name, COUNT(*) AS row_count FROM dim_patient
UNION ALL SELECT 'dim_payer', COUNT(*) FROM dim_payer
UNION ALL SELECT 'dim_provider', COUNT(*) FROM dim_provider
UNION ALL SELECT 'fact_claims', COUNT(*) FROM fact_claims
UNION ALL SELECT 'fact_denials', COUNT(*) FROM fact_denials
UNION ALL SELECT 'fact_payments', COUNT(*) FROM fact_payments
UNION ALL SELECT 'fact_service_lines', COUNT(*) FROM fact_service_lines;

-- 2. Claims row count versus unique Claim_ID
SELECT
    COUNT(*) AS raw_claim_rows,
    COUNT(DISTINCT Claim_ID) AS unique_claims,
    COUNT(*) - COUNT(DISTINCT Claim_ID) AS duplicate_id_occurrences
FROM fact_claims;

-- 3. Check duplicate Claim_IDs in the raw claims table
SELECT Claim_ID, COUNT(*) AS occurrences
FROM fact_claims
GROUP BY Claim_ID
HAVING COUNT(*) > 1
ORDER BY occurrences DESC, Claim_ID;

-- 4. Claims with missing payer/provider/patient dimension matches
-- TEXT key columns may require consistent trimming/casting before joining.
SELECT COUNT(*) AS claims_without_payer_match
FROM fact_claims c
LEFT JOIN dim_payer p ON TRIM(c.Payer_ID) = TRIM(p.Payer_ID)
WHERE p.Payer_ID IS NULL;

SELECT COUNT(*) AS claims_without_provider_match
FROM fact_claims c
LEFT JOIN dim_provider pr ON TRIM(c.Provider_ID) = TRIM(pr.Provider_ID)
WHERE pr.Provider_ID IS NULL;

SELECT COUNT(*) AS claims_without_patient_match
FROM fact_claims c
LEFT JOIN dim_patient pt ON TRIM(c.Patient_ID) = TRIM(pt.Patient_ID)
WHERE pt.Patient_ID IS NULL;

-- 5. Example claim-to-payer join for payer-level analysis
SELECT
    c.Claim_ID,
    c.Payer_ID,
    p.Payer_Name,
    c.AR_Aging_Bucket,
    CAST(c.Outstanding_AR AS DECIMAL(18,2)) AS Outstanding_AR
FROM fact_claims c
LEFT JOIN dim_payer p
    ON TRIM(c.Payer_ID) = TRIM(p.Payer_ID)
LIMIT 25;

-- 6. Check denial records with no matching claim
SELECT COUNT(*) AS unmatched_denial_claim_ids
FROM fact_denials d
LEFT JOIN fact_claims c ON TRIM(d.Claim_ID) = TRIM(c.Claim_ID)
WHERE c.Claim_ID IS NULL;

-- Important: avoid joining payments or service lines directly to claims and then
-- summing claim-level AR without aggregating to Claim_ID first; one-to-many
-- joins can multiply claim rows and inflate totals.
