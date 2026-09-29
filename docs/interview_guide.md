# Interview Guide — NetSuite Financial Reporting Integration

This guide is designed for interviews involving **Snowflake, SQL, Python, NetSuite-style financial data, ELT pipelines, reconciliation, root-cause analysis, and end-to-end pipeline ownership**.

> **Important framing:** This repository is an independent hands-on portfolio project using synthetic data and NetSuite/SuiteAnalytics-style structures. Present the project exactly that way. Do not describe the repository as production NetSuite access or proprietary employer work.

---

## 1. 60–90 Second Project Introduction

> I built this project to model an end-to-end financial reporting integration from NetSuite-style source data into Snowflake. The source layer contains representative financial entities such as transaction headers, transaction lines, accounts, subsidiaries, departments, classes, accounting periods, and currencies.
>
> I used Python to generate and validate synthetic extracts and Snowflake SQL to implement the raw, conformed, reporting, control, reconciliation, and exception-handling layers. The central reporting grain is the transaction line, because financial reporting can become inaccurate very quickly if header- and line-level data are joined without controlling cardinality.
>
> For incremental processing, I used watermark-driven ELT and MERGE patterns so only new or changed records are processed. I also built data-quality and reconciliation controls for record counts, duplicate transaction lines, debit and credit balancing, posting-period alignment, account and subsidiary balances, missing dimension references, and currency consistency.
>
> When a control fails, the design captures the exception for investigation instead of silently passing bad data downstream. I also created RCA queries for common issues such as join multiplication, duplicate rows, orphaned dimensions, period mismatches, late-arriving changes, and pipeline failures. GitHub Actions runs the Python validation and automated tests on every push.

---

## 2. Architecture Walkthrough

Use this sequence when an interviewer asks you to explain the design:

**Source → Validation → RAW → CONFORMED → REPORTING → Reconciliation → Exceptions/RCA**

1. **Source:** SuiteAnalytics-style CSV extracts representing financial entities.
2. **Python validation:** schema, datatype, duplicate, key-integrity, and financial checks.
3. **RAW:** source-aligned Snowflake tables with minimal transformation.
4. **CONFORMED:** normalized dimensions and a transaction-line-level financial fact.
5. **REPORTING:** curated views for financial reporting.
6. **CONTROL:** load watermarks, execution metadata, and reconciliation results.
7. **Exception/RCA:** failed controls are persisted for investigation and remediation.

### Why separate the layers?

A strong answer:

> I separate raw, conformed, reporting, and control responsibilities because each layer has a different purpose. RAW preserves source fidelity, CONFORMED standardizes relationships and business keys, REPORTING exposes consumption-ready logic, and CONTROL provides operational traceability. That separation makes troubleshooting easier because I can identify whether a discrepancy originated in extraction, transformation, dimensional enrichment, or reporting logic.

---

## 3. Key Technical Decisions

### Why transaction-line grain?

> Financial amounts generally live at the transaction-line level. If I join a transaction header directly to multiple line-level or dimension records without understanding cardinality, totals can multiply. I therefore define the financial fact grain explicitly as one row per transaction line and enrich it with header and dimension attributes.

### Why MERGE for incremental ELT?

> MERGE supports idempotent upsert behavior. I can match on the business or source key, update changed rows, insert new rows, and rerun the same batch without creating duplicates. The watermark limits the source data scanned, while MERGE protects the target.

### Why a control table?

> A control table gives the pipeline state. It stores the last successful watermark, run status, timestamps, row counts, and errors. I advance the watermark only after successful validation and load completion so a failed run can be safely replayed.

### Why exception persistence?

> A failed reconciliation should be actionable. Instead of only logging a message, I persist the control name, affected entity or key, expected value, actual value, variance, run identifier, and timestamp. That gives operations and engineering teams a reproducible investigation trail.

---

## 4. Snowflake Interview Questions

### Q: How would you optimize a slow Snowflake query?

> I start with Query Profile rather than guessing. I check scan volume, partition pruning, joins, aggregation cost, spilling, and skew. Then I determine whether the problem is SQL design, data organization, or warehouse sizing. I reduce unnecessary columns and rows early, confirm filters are sargable, remove accidental many-to-many joins, and evaluate clustering only when the table is large enough and query patterns justify it. I treat warehouse scaling as one option, not the first fix, because inefficient SQL will remain inefficient at a larger size.

### Q: What are micro-partitions?

> Snowflake automatically stores table data in immutable micro-partitions and maintains metadata such as value ranges. Query pruning uses that metadata to avoid scanning partitions that cannot satisfy the filter. Good pruning reduces bytes scanned and usually improves both performance and cost.

### Q: Streams and Tasks vs external orchestration?

> Streams and Tasks are useful for Snowflake-native change processing and scheduled SQL workflows. An orchestrator such as Airflow becomes more useful when the workflow spans APIs, files, multiple platforms, complex dependencies, retries, SLAs, or external services. I choose based on operational scope rather than forcing everything into one tool.

### Q: How would you handle schema evolution?

> I detect source schema changes before loading, classify them as compatible or breaking, and prevent silent corruption. Additive nullable columns can often be handled automatically. Datatype changes, renamed keys, or changed relationships should require explicit review, because they may affect transformations, tests, and reporting logic.

---

## 5. SQL Interview Questions

### Q: How do you find duplicate transaction lines?

```sql
SELECT
    transaction_id,
    transaction_line_id,
    COUNT(*) AS row_count
FROM raw.transaction_line
GROUP BY transaction_id, transaction_line_id
HAVING COUNT(*) > 1;
```

Explain it:

> I group by the columns that define the expected grain. Any group with a count greater than one violates uniqueness and becomes an exception candidate.

### Q: How do you keep the latest record when duplicates exist?

```sql
SELECT *
FROM staging_source
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY transaction_id, transaction_line_id
    ORDER BY last_modified_at DESC, ingestion_ts DESC
) = 1;
```

> ROW_NUMBER assigns an order within each business key. QUALIFY keeps only the most recent version without requiring another subquery.

### Q: How would you troubleshoot inflated financial totals after a join?

> First I compare row counts before and after each join. Then I group by the expected fact key and look for keys that appear more than once. I inspect whether the dimension is actually unique on the join key or whether I joined a header-level table to multiple line-level records. Once I identify the cardinality break, I either correct the join key, deduplicate the dimension, aggregate to the required grain before joining, or redesign the model.

### Q: CTE or temporary table?

> I use a CTE for readable logical decomposition when the intermediate result is used within one statement. I consider a temporary table when I need to reuse an expensive intermediate result, inspect it during RCA, or break a large workflow into operational stages.

---

## 6. Python Interview Questions

### Q: What is Python doing in this project?

> Python handles source-side validation and automation. It generates representative synthetic extracts, validates required columns and datatypes, checks key integrity and duplicates, performs financial quality checks, and can parameterize loading into Snowflake. SQL remains responsible for warehouse transformations and reconciliation logic where set-based processing is more appropriate.

### Q: How would you make the Python loader production-ready?

> I would separate configuration from code, use secrets management instead of hard-coded credentials, add structured logging and correlation IDs, make loads idempotent, implement bounded retries with backoff for transient failures, emit operational metrics, validate files before loading, and make failure states explicit so orchestration can retry or alert safely.

### Q: How do you prevent partial loads?

> I design the process so the watermark is not advanced until the entire batch succeeds. Depending on the loading pattern, I can load into staging tables first, validate the batch, and then MERGE into the target. If validation fails, the target remains unchanged or the run remains replayable.

---

## 7. NetSuite / Financial Data Questions

### Q: What NetSuite-style entities matter most for financial reporting?

> The core model includes transaction headers, transaction lines, accounts, subsidiaries, accounting periods, currencies, departments, and classes. The exact schema depends on the extraction method and configuration, but the important engineering principle is understanding the source grain and relationships before building reporting transformations.

### Q: Why are accounting periods important?

> Financial reporting is period-driven, and posting date alone may not be sufficient. I validate that transactions map to the expected accounting period and investigate differences between transaction dates, posting periods, closed periods, and reporting cutoffs.

### Q: How would you reconcile source and Snowflake?

> I use multiple control levels rather than one grand total. I compare record counts, key uniqueness, debit and credit totals where applicable, totals by account, subsidiary and period, missing dimensions, and final reporting totals. When there is a variance, I progressively narrow the comparison until I identify the specific transaction or relationship causing it.

### Q: How do you handle late-arriving updates?

> The extraction window should include a reliable modification timestamp or a controlled lookback window. The target uses MERGE so previously loaded keys can be updated. I only move the successful watermark after processing and validation complete.

---

## 8. Reconciliation and Root-Cause Analysis

A good RCA structure is:

**Detect → Scope → Compare → Isolate → Explain → Correct → Prevent**

### Example scenario: source total is $5.2M but reporting shows $5.35M

> I first confirm the discrepancy is reproducible and identify the affected period, subsidiary, and account range. I compare source and target counts and totals at progressively lower grains. If row counts increased after enrichment, I test for join multiplication. If counts match, I compare amounts and transformation logic, then inspect currency, posting-period, and sign handling. Once I isolate the root cause, I correct the transformation or data relationship, rerun the affected batch, reconcile again, and add a regression test or control so the same issue is detected automatically in the future.

### Common RCA checks in this repository

- Duplicate transaction lines
- Many-to-many join multiplication
- Missing dimension keys
- Inactive dimensions referenced by posted transactions
- Accounting-period mismatch
- Currency mismatch
- Unbalanced journal-style activity
- Late-arriving source changes
- Failed or incomplete pipeline runs

---

## 9. Behavioral / Ownership Questions

### Q: Tell me about a difficult data-quality issue.

Use STAR:

**Situation:** A downstream financial total does not reconcile with the source.

**Task:** Determine whether the problem is extraction, transformation, relationship logic, or reporting.

**Action:** Compare counts and amounts by layer, narrow the variance by period/account/subsidiary, test uniqueness and join cardinality, inspect the affected source keys, correct the logic, replay the batch, and add a preventive control.

**Result:** The data is reconciled, the root cause is documented, and future occurrences are caught by an automated validation rather than by a business user.

### Q: How do you work independently with business stakeholders?

> I start by converting the business question into measurable data rules: required grain, source of truth, accounting definition, expected refresh frequency, acceptance criteria, and reconciliation tolerance. I document assumptions early, show sample outputs before finalizing the model, and use reconciliation evidence when discussing discrepancies so the conversation stays objective.

### Q: What do you do when requirements are unclear?

> I do not start by coding the ambiguity. I identify the decision that is missing, provide concrete examples of how different interpretations affect the result, and confirm the expected business rule. For financial data, small semantic differences can materially change totals, so I make those assumptions explicit.

---

## 10. End-to-End Ownership Answer

### Q: Walk me through how you would own this pipeline from requirement to production.

> I would begin with source discovery and business definitions: the financial grain, required entities, reporting rules, refresh SLA, and reconciliation expectations. Next I would profile the source and document key relationships and change behavior.
>
> I would design raw, conformed, reporting, and control layers, define incremental keys and watermarks, and build validation before transformation. After that I would implement the transformations and MERGE logic, followed by financial reconciliation controls and exception capture.
>
> Before release, I would test normal loads, retries, duplicates, late-arriving changes, missing dimensions, schema changes, and failure recovery. I would add CI checks, operational logging, run metadata, alerts, and a rollback or replay procedure. After deployment, I would monitor freshness, row counts, reconciliation status, query performance, and recurring exceptions.

---

## 11. Critical Questions You May Be Asked

### Why did you build this project?

> I wanted a hands-on implementation that demonstrates the difficult parts of financial data engineering rather than only a simple ingestion demo: source grain, relational modeling, incremental ELT, financial reconciliation, exception handling, and RCA.

### Is this connected to a live NetSuite environment?

> No. This repository intentionally uses synthetic data and NetSuite/SuiteAnalytics-style structures. The value of the project is demonstrating the engineering patterns and financial controls without exposing proprietary data or credentials.

### What would change with a real NetSuite source?

> I would replace the synthetic extract generator with the approved enterprise extraction mechanism, preserve source identifiers and modification timestamps, add source-specific rate-limit and retry behavior if applicable, validate actual schema metadata, and integrate secrets, orchestration, monitoring, and environment promotion controls.

### What is the hardest part of the project?

> The hardest part is not moving rows into Snowflake. It is preserving the correct financial grain and proving that transformed reporting outputs reconcile back to the source. Most serious issues come from relationship assumptions, duplicate versions, period logic, currency logic, or incomplete incremental processing.

---

## 12. Questions to Ask the Interviewer

1. What is the current NetSuite-to-Snowflake extraction mechanism?
2. Which financial domains create the most reconciliation issues today?
3. What is considered the authoritative source when NetSuite and downstream reporting disagree?
4. How are NetSuite schema or saved-search changes communicated to the data team?
5. What are the expected data freshness and month-end close SLAs?
6. How are failed reconciliations triaged and owned?
7. Which Snowflake workloads currently have the highest cost or performance pressure?
8. How much of the role is new architecture versus production support and RCA?
9. What testing and deployment process is used for financial transformation changes?
10. What would success look like in the first 90 days?

---

## 13. Repository Files to Reference During the Interview

| Topic | File |
|---|---|
| Environment / schemas | `sql/00_setup.sql` |
| Raw tables | `sql/01_raw_tables.sql` |
| Conformed model | `sql/02_conformed_models.sql` |
| Incremental MERGE | `sql/03_incremental_elt.sql` |
| Reporting views | `sql/04_reporting_views.sql` |
| Reconciliation | `sql/05_reconciliation.sql` |
| RCA queries | `sql/06_rca_queries.sql` |
| Exception capture | `sql/07_exception_capture.sql` |
| Synthetic data | `src/generate_sample_data.py` |
| Data validation | `src/validate_extracts.py` |
| Snowflake loader | `src/load_to_snowflake.py` |
| Automated tests | `tests/test_validations.py` |
| Data model | `docs/data_model.md` |
| RCA playbook | `docs/rca_playbook.md` |

---

## 14. Final 30-Second Summary

> This project demonstrates how I approach financial data engineering end to end: understand the source grain, preserve source fidelity, build controlled incremental transformations, validate relationships, reconcile financial results, capture exceptions, and make failures diagnosable. Snowflake and SQL handle the warehouse transformations, Python supports validation and automation, and CI verifies the project continuously. The focus is not only building the pipeline, but proving that the financial output is complete, accurate, traceable, and recoverable.
