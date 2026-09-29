# Financial Data RCA Playbook

## 1. Reporting totals suddenly increase

**Likely cause:** join-cardinality multiplication.

**Checks:**
- Compare fact row counts before and after each dimension join.
- Verify dimension business keys are unique.
- Inspect duplicated raw dimension versions.

**Remediation:**
- Deduplicate dimensions using latest-modified logic.
- Join to conformed dimensions rather than raw history.
- Add uniqueness tests on dimension keys.

## 2. Duplicate transaction lines

**Likely cause:** repeated extracts, late source updates, or non-idempotent loading.

**Checks:**
- Group by `(transaction_id, line_id)`.
- Compare `last_modified_at` and ingestion timestamps.

**Remediation:**
- Use MERGE/upsert semantics.
- Deduplicate stage data before merging.
- Track source watermarks and run IDs.

## 3. Missing account, subsidiary, department, or class

**Likely cause:** late-arriving dimensions, deleted/inactive source records, or extract sequencing.

**Checks:**
- Anti-join fact rows to each dimension.
- Compare source extract timestamps.

**Remediation:**
- Load dimensions before facts.
- Reprocess affected fact partitions after late dimensions arrive.
- Route unresolved rows to an exception dataset.

## 4. Posting-period mismatch

**Likely cause:** incorrect period mapping or backdated transaction posting.

**Checks:**
- Compare transaction date with accounting-period start/end dates.
- Check whether the period is closed.

**Remediation:**
- Confirm expected accounting policy.
- Correct period mapping upstream or apply controlled restatement logic.

## 5. Currency mismatch

**Likely cause:** transaction currency differs from subsidiary base currency without a valid exchange rate.

**Checks:**
- Compare transaction currency with subsidiary base currency.
- Validate exchange rate is positive and populated.

**Remediation:**
- Load missing exchange-rate data.
- Quarantine unsupported currency combinations.

## 6. Journal does not balance

**Likely cause:** missing line, duplicate line, sign handling, or partial incremental load.

**Checks:**
- Sum debit and credit by journal transaction.
- Compare source and target line counts.
- Verify all lines share the same incremental window.

**Remediation:**
- Re-extract the full journal.
- Use transaction-consistent watermarking or reconciliation-based replay.

## 7. Pipeline failure

**Checks:**
- Inspect `CONTROL.LOAD_CONTROL` status/error.
- Confirm source schema and datatypes.
- Re-run schema validation before loading.
- Compare watermark bounds to source timestamps.

**Remediation:**
- Fix the source/target contract or coercion rule.
- Re-run idempotently from the last successful watermark.
