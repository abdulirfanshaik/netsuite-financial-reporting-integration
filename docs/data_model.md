# Data Model

## Grain

`CONFORMED.FACT_GL_LINE` is modeled at one row per `(transaction_id, line_id)` after deduplication by latest `last_modified_at`.

## Relationships

| Source entity | Key | Relationship |
|---|---|---|
| Transaction header | `transaction_id` | 1-to-many with transaction lines |
| Transaction line | `(transaction_id, line_id)` | Financial fact grain |
| Account | `account_id` | Many lines to one account |
| Subsidiary | `subsidiary_id` | Many lines to one legal/entity dimension |
| Department | `department_id` | Optional line dimension |
| Class | `class_id` | Optional line dimension |
| Accounting period | `accounting_period_id` | Many transactions to one posting period |
| Currency | `currency_id` | Many transactions/lines to one currency |

## Modeling Assumptions

1. Transaction header stores posting date, posting period, transaction type, primary subsidiary, currency, exchange rate, and posting flag.
2. Transaction line stores accounting distributions, including account and debit/credit values.
3. A line-level subsidiary or currency overrides the header when supplied.
4. Latest `last_modified_at` wins when duplicate source versions exist.
5. Journal-style transactions are expected to balance debit and credit to a configurable tolerance.
6. Reporting views include only posted activity.
7. Synthetic sample data is intentionally small and understandable; production systems would require stronger CDC, history, and security controls.

## Layering

### RAW
Near-source structures with minimal normalization and ingestion metadata.

### CONFORMED
Deduplicated dimensions and a transaction-line fact table with consistent types and business keys.

### REPORTING
Financial views that expose income-statement and balance-sheet-friendly aggregations.

### CONTROL
Pipeline execution metadata and reconciliation exceptions.


## Interview Talking Points

When presenting this model in an interview, emphasize the explicit transaction-line grain, controlled header-to-line relationships, deduplicated dimensions, posted-only reporting, and the separation between RAW, CONFORMED, REPORTING, and CONTROL layers.

Key files to reference:
- `sql/02_conformed_models.sql`
- `sql/04_reporting_views.sql`
- `sql/05_reconciliation.sql`
- `docs/interview_guide.md`
