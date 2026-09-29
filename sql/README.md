# SQL Layer

This directory contains the ordered Snowflake SQL implementation for the financial reporting integration.

Execution order:

1. `00_setup.sql`
2. `01_raw_tables.sql`
3. `02_conformed_models.sql`
4. `03_incremental_elt.sql`
5. `04_reporting_views.sql`
6. `05_reconciliation.sql`
7. `06_rca_queries.sql`
8. `07_exception_capture.sql`

The scripts cover environment setup, raw ingestion, conformed models, incremental ELT, reporting, reconciliation, root-cause analysis, and exception capture.
