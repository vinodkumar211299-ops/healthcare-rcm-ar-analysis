# Project Data

This project uses synthetic US healthcare revenue-cycle management (RCM) data created for portfolio and learning purposes. The data is not real patient or provider data.

The seven source tables are:

- `dim_patient.csv`
- `dim_payer.csv`
- `dim_provider.csv`
- `fact_claims.csv`
- `fact_denials.csv`
- `fact_payments.csv`
- `fact_service_lines.csv`

## Data sharing notes

The source CSVs are maintained separately from the project code. Before publishing any CSVs, review the columns and values, remove unnecessary direct identifiers from the public copies, and confirm the files are synthetic.

The original payment file and `fact_payments_corrected.csv` serve different purposes. The corrected file contains a documented synthetic-data normalization of `Paid_Amount` at claim level; it is not genuine transaction history. Keep the original file unchanged for traceability.

Do not place database credentials, connection strings with passwords, or other secrets in this repository.
