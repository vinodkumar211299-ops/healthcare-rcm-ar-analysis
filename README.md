# Healthcare RCM: Accounts Receivable Aging & Denial Analysis

> **Portfolio project \| SQL · Power BI · Python · Statistics**
>
> **Status:** Analysis and documentation are being finalized. Reported
> figures below must be reconciled across SQL, Python, and Power BI
> before this README is treated as a final validated release.

## 1. Project overview

Healthcare revenue-cycle teams need to understand where accounts
receivable (AR) is accumulating, how much is aging, and which claims or
operational areas deserve follow-up.

This project investigates outstanding AR by aging bucket, payer,
provider, denial-record presence, and payment-record presence. The goal
is to turn claim-level data into clear investigation priorities for an
RCM team.

**Business question:** Where is outstanding AR concentrated, and what
should the RCM team investigate first?

### Objectives

-   Assess the quality and structure of the source datasets.
-   Analyze outstanding AR across aging buckets.
-   Compare AR and denial patterns across payers and providers.
-   Examine whether 120+ day AR has a matching record in the denial
    dataset.
-   Check payment-record coverage for claims.
-   Validate selected results independently and translate findings into
    practical follow-up recommendations.

## 2. Tools and how they were used

  -----------------------------------------------------------------------
  Tool                                Role in the project
  ----------------------------------- -----------------------------------
  SQL (MySQL)                         Explore data, join related tables,
                                      group and aggregate records,
                                      calculate reference KPIs, and
                                      investigate payer/provider
                                      patterns.

  Power Query                         Profile, clean, type, and shape
                                      data for analysis.

  Power BI and DAX                    Build the data model, define
                                      reusable measures, and present AR
                                      aging and denial patterns in a
                                      dashboard.

  Python and Pandas                   Independently inspect data, check
                                      key uniqueness and relationships,
                                      calculate selected summaries, and
                                      reconcile results.

  Statistics                          Describe the distribution of
                                      outstanding AR and flag potential
                                      outliers for review.

  Excel                               Organize project documentation and
                                      final quality checks.
  -----------------------------------------------------------------------

## 3. Data architecture

The project uses seven related datasets:

  -----------------------------------------------------------------------
  Dataset                             Purpose
  ----------------------------------- -----------------------------------
  Claims                              Claim-level dates, amounts, status,
                                      and outstanding AR context.

  Denials                             Denial records and reason codes
                                      associated with claims.

  Payments                            Payment activity associated with
                                      claims.

  Service-line items                  Procedure/service detail at the
                                      claim service-line level.

  Patients                            Patient dimension attributes.

  Payers                              Payer dimension attributes.

  Providers                           Provider dimension attributes.
  -----------------------------------------------------------------------

### Data-quality work

-   The original claims dataset contained **50,025 rows** and **25
    duplicate Claim_ID occurrences**. A cleaned reference table
    contained **50,000 unique Claim_IDs**.
-   Data-quality checks included row counts, duplicate/key checks, data
    types, nulls, relationships, and financial/date logic.
-   The raw claims source was retained while a distinct cleaned
    reference was used for analysis.
-   Negative financial values and year-boundary/date logic were
    investigated; such values should not be labelled errors without
    checking credit, adjustment, and sign conventions.
-   Relationships were checked using key matching. Before publication,
    the final model should also be checked for dimension-key uniqueness,
    expected relationship cardinality, and row multiplication after
    joins.

## 4. Reported headline results

The following are the project's **reported reference results**. Re-run
the final SQL/Python/Power BI reconciliation before treating them as
publication-verified.

  -------------------------------------------------------------------------
  Metric                             Reported result Definition / note
  --------------------- ---------------------------- ----------------------
  Unique claims                               50,000 Distinct Claim_IDs in
                                                     the cleaned claims
                                                     reference.

  Claims represented in                        8,942 Distinct Claim_IDs in
  denial table                                       the denial dataset.

  Denial rate                                 17.88% 8,942 / 50,000,
                                                     rounded. This is based
                                                     on denial-table
                                                     presence, not solely
                                                     the status field in
                                                     the claims table.

  Total outstanding AR               \$37,218,788.69 Reported project
                                                     total; confirm the
                                                     final financial logic
                                                     and treatment of
                                                     adjustments/credits.

  Outstanding AR aged                \$24,526,260.65 Reported aging result;
  120+ days                                          confirm the date basis
                                                     and bucket boundaries.

  120+ day AR with a                  \$4,375,152.16 Classified by Claim_ID
  denial-table match                                 presence in the denial
                                                     dataset.

  120+ day AR without a              \$20,151,108.49 Means no matching
  denial-table match                                 record was found in
                                                     the denial dataset; it
                                                     does not prove the
                                                     claim was never
                                                     denied.
  -------------------------------------------------------------------------

The reported 120+ day groups sum to **\$24,526,260.65**, with a reported
reconciliation difference of **\$0.00**. The no-matching-denial-record
group represents approximately **82.16%** of the 120+ day balance.
Confirm this split after the final cross-tool reconciliation.

## 5. Aging analysis

Reported AR aging buckets:

  Aging bucket     Reported outstanding AR
  -------------- -------------------------
  0--30 days                \$3,553,411.48
  31--60 days               \$3,006,346.71
  61--90 days               \$3,047,583.15
  91--120 days              \$3,085,186.70
  120+ days                \$24,526,260.65

The 120+ day bucket is the largest reported concentration, at
approximately **65.90%** of the reported total outstanding AR. This is a
priority for further investigation; aging by itself does not identify
the cause of delay or prove that the full balance is recoverable.

**Validation required:** Re-add all five buckets and compare them with
the reported total AR of \$37,218,788.69. Resolve any difference before
publishing the final dashboard figures.

## 6. Denial and provider investigation

### Denial-table interpretation

The project compared 120+ day AR based on whether each claim had a
matching record in the denial dataset. This classification is useful for
segmentation, but it must be described precisely:

-   **With denial-table match:** a matching Claim_ID exists in the
    denial dataset.
-   **Without denial-table match:** no matching Claim_ID exists in the
    denial dataset.

The second group should not automatically be described as claims that
could never be denied or as claims with no denial-related issue.

### Provider_0074

The recorded investigation for Provider_0074 (Dermatology, Dallas)
reported:

-   Total claims: **486**
-   Claims with a matching denial record: **110**
-   Denial-record rate: **22.63%**

This is higher than the reported overall rate of 17.88% and is a signal
for targeted review---not proof that the provider caused the denials.
The investigation also highlighted CO-04 as a coding-related denial
reason to review against the affected claim details and applicable payer
requirements. The appropriate correction must be determined case by
case.

## 7. Payment-record investigation

The reported payment coverage check found:

-   **42,920** distinct claims with a payment record.
-   **7,080** distinct claims without a payment record.

A payment record does **not** prove that a claim was fully paid or
partially paid. To assess the remaining balance, compare claim-level
billed, allowed, paid, adjustment, and outstanding amounts using the
project's validated financial definitions. Also account for the
possibility of multiple payment transactions per claim.

For 120+ day non-denial AR, the reported split was:

  Group                           Reported AR
  ------------------------- -----------------
  With payment records        \$17,231,629.09
  Without payment records      \$2,919,479.40
  Total                       \$20,151,108.49

These values should be reconfirmed against the final query and data
model before publication.

## 8. Statistics and outlier screening

Descriptive statistics reported for claim-level outstanding AR included:

-   Median: approximately **\$563.37**
-   Third quartile (Q3): approximately **\$970.22**
-   Maximum: approximately **\$11,332.93**
-   IQR upper screening threshold: approximately **\$1,969.45**
-   Potential outliers flagged by the IQR rule: **2,526 claims** (about
    **5.05%**)

These are screening results, not evidence that the flagged claims are
incorrect. High values should be reviewed against claim context and
business rules; they should not be automatically removed.

## 9. Business recommendations

Based on the reported patterns, an RCM team could consider:

1.  Prioritize work queues for claims aged 120+ days.
2.  Segment old AR by payer, provider, denial-table presence, and
    payment-record presence.
3.  Review old balances without a matching denial record instead of
    focusing only on denials.
4.  For claims with payment activity, verify payment posting,
    adjustments, and the remaining balance.
5.  Investigate provider-level denial patterns and review CO-04 cases
    against coding and payer requirements.
6.  Track follow-up outcomes over time to determine whether actions
    reduce aged AR.

These are recommendations for investigation and operational
prioritization. The project does **not** establish that collections
improved, that a specific amount was recovered, or that one factor
definitively caused AR to accumulate.

## 10. Limitations and interpretation

-   The analysis identifies concentrations and investigation leads; it
    does not establish the definitive cause of every outstanding
    balance.
-   A claim's absence from the denial dataset means only that no
    matching record was found in that dataset.
-   A payment record does not establish full or partial payment without
    amount-level reconciliation.
-   To claim that AR **increased over time**, compare consistent AR
    measures across multiple time periods. A large aging bucket alone
    shows concentration, not a trend.
-   Provider comparisons are descriptive and should consider claim
    volume, specialty, payer mix, and case mix before drawing
    conclusions.
-   The reported metrics must be reconciled across SQL, Python, and
    Power BI before final public release.
-   Use synthetic or appropriately anonymized data only. Do not publish
    patient names, Tax IDs, credentials, or other sensitive information.

## 11. Suggested repository structure

Organize the repository as the project is finalized:

``` text
healthcare-rcm-ar-analysis/
├── README.md
├── sql/
│   ├── 01_data_quality_checks.sql
│   ├── 02_ar_aging_analysis.sql
│   ├── 03_denial_analysis.sql
│   ├── 04_payer_provider_analysis.sql
│   └── 05_payment_reconciliation.sql
├── python/
│   └── project1_validation.py
├── powerbi/
│   └── dashboard_screenshots/
├── documentation/
│   ├── project_documentation.xlsx
│   └── interview_presentation.pptx
└── data/
    └── README.md
```

This is a **suggested structure**, not a claim that all files are
already present. Add only files that exist and have been reviewed. Do
not upload raw data unless it is synthetic, safe to share, and
appropriate for public release.

## 12. Reproducing the analysis

1.  Review the data dictionary and table grain for each dataset.
2.  Load the approved project datasets into a local database or analysis
    environment.
3.  Run the documented SQL checks and analyses.
4.  Run the Python validation script with the correct local file paths
    and connection settings.
5.  Compare the definitions and outputs across SQL, Python, and Power
    BI.
6.  Reconcile row counts, unique claim counts, denial rate, total AR,
    aging buckets, and the 120+ day split.
7.  Document any unresolved discrepancies instead of silently changing a
    figure.

Local paths, credentials, and environment-specific connection settings
should be supplied locally and never committed to GitHub.

## 13. Project takeaway

This project demonstrates an end-to-end approach to a healthcare RCM
analytics question: prepare related datasets, investigate AR aging and
denial patterns, validate selected findings, and translate results into
practical follow-up priorities. Its strongest portfolio value comes from
transparent definitions, reproducible checks, clear business reasoning,
and honest limitations---not the number of queries or functions used.

------------------------------------------------------------------------

**Publication status:** Working draft. Complete the final
SQL/Python/Power BI reconciliation, verify definitions and source files,
and review privacy before treating this README as final.

