
import pandas as pd
from pathlib import Path

# 1. Dataset folder
DATA_DIR = Path(r"C:\vinod")

# 2. Load all seven tables
tables = {
    "dim_patient": pd.read_csv(DATA_DIR / "dim_patient.csv"),
    "dim_payer": pd.read_csv(DATA_DIR / "dim_payer.csv"),
    "dim_provider": pd.read_csv(DATA_DIR / "dim_provider.csv"),
    "fact_claims": pd.read_csv(DATA_DIR / "fact_claims.csv"),
    "fact_denials": pd.read_csv(DATA_DIR / "fact_denials.csv"),
    "fact_payments": pd.read_csv(DATA_DIR / "fact_payments.csv"),
    "fact_service_lines": pd.read_csv(DATA_DIR / "fact_service_lines.csv")
}

# 3. Data quality checks for every table
for table_name, df in tables.items():

    print("\n" + "=" * 55)
    print("TABLE:", table_name)
    print("=" * 55)

    print("Shape:", df.shape)
    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nExact duplicate rows:", df.duplicated().sum())

    print("\nFirst 5 rows:")
    print(df.head())

print("\nALL SEVEN TABLES VALIDATED.")

# Check claims-to-payer relationship

print("\n--- CLAIMS TO PAYER CHECK ---")

print(
    "Unique payer IDs in claims:",
    tables["fact_claims"]["Payer_ID"].nunique()
)

print(
    "Unique payer IDs in payer table:",
    tables["dim_payer"]["Payer_ID"].nunique()
)

print(
    "Payer IDs in claims missing from payer table:",
    (~tables["fact_claims"]["Payer_ID"].isin(
        tables["dim_payer"]["Payer_ID"]
    )).sum()
)

print("\n--- CLAIMS TO PROVIDER CHECK ---")

print(
    "Unique provider IDs in claims:",
    tables["fact_claims"]["Provider_ID"].nunique()
)

print(
    "Unique provider IDs in provider table:",
    tables["dim_provider"]["Provider_ID"].nunique()
)

print(
    "Provider IDs in claims missing from provider table:",
    (~tables["fact_claims"]["Provider_ID"].isin(
        tables["dim_provider"]["Provider_ID"]
    )).sum()
)

print("\n--- CLAIMS TO PATIENT CHECK ---")

print(
    "Unique patient IDs in claims:",
    tables["fact_claims"]["Patient_ID"].nunique()
)

print(
    "Unique patient IDs in patient table:",
    tables["dim_patient"]["Patient_ID"].nunique()
)

print(
    "Patient IDs in claims missing from patient table:",
    (~tables["fact_claims"]["Patient_ID"].isin(
        tables["dim_patient"]["Patient_ID"]
    )).sum()
)

print("\n--- DENIALS TO CLAIMS CHECK ---")

print(
    "Unique claim IDs in denials:",
    tables["fact_denials"]["Claim_ID"].nunique()
)

print(
    "Unique claim IDs in claims:",
    tables["fact_claims"]["Claim_ID"].nunique()
)

print(
    "Denial records with unmatched claim IDs:",
    (
        ~tables["fact_denials"]["Claim_ID"].isin(
            tables["fact_claims"]["Claim_ID"]
        )
    ).sum()
)

print("\n--- PAYMENTS TO CLAIMS CHECK ---")

print(
    "Unique claim IDs in payments:",
    tables["fact_payments"]["Claim_ID"].nunique()
)

print(
    "Unique claim IDs in claims:",
    tables["fact_claims"]["Claim_ID"].nunique()
)

print(
    "Payment records with unmatched claim IDs:",
    (
        ~tables["fact_payments"]["Claim_ID"].isin(
            tables["fact_claims"]["Claim_ID"]
        )
    ).sum()
)

print("\n--- SERVICE LINES TO CLAIMS CHECK ---")

print(
    "Unique claim IDs in service lines:",
    tables["fact_service_lines"]["Claim_ID"].nunique()
)

print(
    "Unique claim IDs in claims:",
    tables["fact_claims"]["Claim_ID"].nunique()
)

print(
    "Service-line records with unmatched claim IDs:",
    (
        ~tables["fact_service_lines"]["Claim_ID"].isin(
            tables["fact_claims"]["Claim_ID"]
        )
    ).sum()
)


# STEP 1: Prepare the claims dataset

claims_df = tables["fact_claims"].drop_duplicates(
    subset=["Claim_ID"]
).copy()

# STEP 2: Convert Outstanding_AR into a numeric column

claims_df["Outstanding_AR"] = pd.to_numeric(
    claims_df["Outstanding_AR"],
    errors="coerce"
)

# STEP 3: Calculate the KPIs

print("\n--- CLAIMS AND AR KPI VALIDATION ---")

print("Unique claims:", claims_df["Claim_ID"].nunique())

print(
    "Total Outstanding AR:",
    round(claims_df["Outstanding_AR"].sum(), 2)
)

# STEP 4: Calculate AR for each aging bucket

print("\nAR by aging bucket:")

print(
    claims_df.groupby(
        "AR_Aging_Bucket",
        dropna=False
    )["Outstanding_AR"]
    .sum()
    .sort_index()
)

# STEP 5: Validate denial KPIs

denials_df = tables["fact_denials"]

total_claims = claims_df["Claim_ID"].nunique()

total_denial_records = len(denials_df)

denied_claims = denials_df["Claim_ID"].nunique()

denial_rate = denied_claims / total_claims * 100

print("\n--- DENIAL KPI VALIDATION ---")

print("Total claims:", total_claims)
print("Total denial records:", total_denial_records)
print("Distinct claims with denial records:", denied_claims)
print("Denial rate (%):", round(denial_rate, 2))

# STEP 6: Denied amount and reason-code analysis

denials_df["Denied_Amount"] = pd.to_numeric(
    denials_df["Denied_Amount"],
    errors="coerce"
)

print("\n--- DENIED AMOUNT VALIDATION ---")

print(
    "Total denied amount:",
    round(denials_df["Denied_Amount"].sum(), 2)
)

print(
    "Average denied amount:",
    round(denials_df["Denied_Amount"].mean(), 2)
)

print("\nDenial records by reason code:")

print(
    denials_df.groupby("Denial_Reason_Code")
    .size()
    .sort_values(ascending=False)
)

print("\nDenied amount by reason code:")

print(
    denials_df.groupby("Denial_Reason_Code")["Denied_Amount"]
    .sum()
    .sort_values(ascending=False)
)

# STEP 7: Investigate 120+ days outstanding AR

old_ar = claims_df[
    claims_df["AR_Aging_Bucket"] == "120+"
].copy()

# Identify claims represented in the denial table
denied_claim_ids = denials_df["Claim_ID"].dropna().unique()

old_ar["Denial_Flag"] = old_ar["Claim_ID"].isin(
    denied_claim_ids
)

# Calculate denied and non-denied AR
denied_old_ar = old_ar.loc[
    old_ar["Denial_Flag"], "Outstanding_AR"
].sum()

non_denied_old_ar = old_ar.loc[
    ~old_ar["Denial_Flag"], "Outstanding_AR"
].sum()

total_old_ar = old_ar["Outstanding_AR"].sum()

print("\n--- 120+ DAYS AR INVESTIGATION ---")

print("Total 120+ AR:", round(total_old_ar, 2))
print("Denied 120+ AR:", round(denied_old_ar, 2))
print("Non-denied 120+ AR:", round(non_denied_old_ar, 2))

print(
    "Non-denied share (%):",
    round(non_denied_old_ar / total_old_ar * 100, 2)
    if total_old_ar else 0
)

print(
    "Reconciliation difference:",
    round(total_old_ar - denied_old_ar - non_denied_old_ar, 2)
)

# STEP 8: Payer-level AR analysis with payer names

print("\n--- PAYER AR ANALYSIS ---")

# Merge claims with payer dimension
claims_payer = claims_df.merge(
    tables["dim_payer"][["Payer_ID", "Payer_Name"]],
    on="Payer_ID",
    how="left",
    validate="many_to_one"
)

# Total AR by payer
payer_ar = (
    claims_payer.groupby("Payer_Name", dropna=False)["Outstanding_AR"]
    .sum()
    .sort_values(ascending=False)
)

print("\nTop 10 payers by Outstanding AR:")
print(payer_ar.head(10))

# 120+ days AR by payer
old_claims_payer = claims_payer[
    claims_payer["AR_Aging_Bucket"] == "120+"
]

payer_old_ar = (
    old_claims_payer.groupby("Payer_Name", dropna=False)["Outstanding_AR"]
    .sum()
    .sort_values(ascending=False)
)

print("\nTop 10 payers by 120+ AR:")
print(payer_old_ar.head(10))


# STEP 9: Provider-level AR and denial analysis

print("\n--- PROVIDER ANALYSIS ---")

claims_provider = claims_df.merge(
    tables["dim_provider"][
        ["Provider_ID", "Provider_Name", "Specialty", "Location"]
    ],
    on="Provider_ID",
    how="left",
    validate="many_to_one"
)

denied_claim_ids = denials_df["Claim_ID"].dropna().unique()

claims_provider["Has_Denial_Record"] = (
    claims_provider["Claim_ID"].isin(denied_claim_ids)
)

provider_summary = claims_provider.groupby(
    ["Provider_ID", "Provider_Name", "Specialty", "Location"],
    dropna=False
).agg(
    Total_Claims=("Claim_ID", "nunique"),
    Total_AR=("Outstanding_AR", "sum"),
    Claims_With_Denial=("Has_Denial_Record", "sum")
)

provider_summary["Denial_Rate_Pct"] = (
    provider_summary["Claims_With_Denial"]
    / provider_summary["Total_Claims"] * 100
).round(2)

print("\nTop 10 providers by Outstanding AR:")
print(provider_summary.sort_values("Total_AR", ascending=False).head(10))

print("\nTop 10 providers by denial rate:")
print(
    provider_summary.sort_values(
        "Denial_Rate_Pct", ascending=False
    ).head(10)
)

print("\nProvider_0074 investigation:")

if "Provider_0074" in provider_summary.index.get_level_values("Provider_ID"):
    print(provider_summary.xs("Provider_0074", level="Provider_ID"))
else:
    print("Provider_0074 not found. Check Provider_ID data type.")


payments_df = tables["fact_payments"]

print("Payments loaded:", payments_df.shape)


# STEP 10: PAYMENT COVERAGE ANALYSIS

print("\n--- PAYMENT COVERAGE ANALYSIS ---")

payment_claim_ids = payments_df["Claim_ID"].dropna().unique()

claims_df["Has_Payment_Record"] = (
    claims_df["Claim_ID"].isin(payment_claim_ids)
)

claims_with_payment = claims_df["Has_Payment_Record"].sum()
claims_without_payment = (~claims_df["Has_Payment_Record"]).sum()

print("Total unique claims:", claims_df["Claim_ID"].nunique())
print("Claims with payment records:", claims_with_payment)
print("Claims without payment records:", claims_without_payment)

print(
    "Payment record coverage (%):",
    round(claims_with_payment / len(claims_df) * 100, 2)
)

# STEP 11: Payment coverage in 120+ days non-denied AR

print("\n--- OLD NON-DENIED AR PAYMENT INVESTIGATION ---")

old_non_denied = old_ar[
    ~old_ar["Denial_Flag"]
].copy()

old_non_denied["Has_Payment_Record"] = (
    old_non_denied["Claim_ID"].isin(payment_claim_ids)
)

ar_with_payment = old_non_denied.loc[
    old_non_denied["Has_Payment_Record"],
    "Outstanding_AR"
].sum()

ar_without_payment = old_non_denied.loc[
    ~old_non_denied["Has_Payment_Record"],
    "Outstanding_AR"
].sum()

print("Total 120+ non-denied AR:",
      round(old_non_denied["Outstanding_AR"].sum(), 2))

print("AR with payment records:", round(ar_with_payment, 2))
print("AR without payment records:", round(ar_without_payment, 2))

print("Reconciliation difference:",
      round(
          old_non_denied["Outstanding_AR"].sum()
          - ar_with_payment
          - ar_without_payment,
          2
      ))


print("\n--- PROVIDER_0074 INVESTIGATION ---")

provider_0074 = tables["dim_provider"][
    tables["dim_provider"]["Provider_Name"] == "Provider_0074"
]

print(
    provider_0074[
        ["Provider_ID", "Provider_Name", "Specialty", "Location"]
    ]
)
print("\n--- OUTSTANDING AR: DESCRIPTIVE STATISTICS ---")
print(claims_df["Outstanding_AR"].describe().round(2))

# STEP 13: Potential outlier investigation

Q1 = claims_df["Outstanding_AR"].quantile(0.25)
Q3 = claims_df["Outstanding_AR"].quantile(0.75)

IQR = Q3 - Q1

upper_limit = Q3 + 1.5 * IQR
lower_limit = Q1 - 1.5 * IQR

outliers = claims_df[
    (claims_df["Outstanding_AR"] < lower_limit)
    | (claims_df["Outstanding_AR"] > upper_limit)
]

print("\n--- OUTLIER INVESTIGATION ---")
print("Q1:", round(Q1, 2))
print("Q3:", round(Q3, 2))
print("IQR:", round(IQR, 2))
print("Lower limit:", round(lower_limit, 2))
print("Upper limit:", round(upper_limit, 2))
print("Potential outlier claims:", len(outliers))

print("\nTop 10 highest outstanding AR claims:")
print(
    outliers.sort_values(
        "Outstanding_AR", ascending=False
    )[["Claim_ID", "Outstanding_AR"]].head(10)
)
