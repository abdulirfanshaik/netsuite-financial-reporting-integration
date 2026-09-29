from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass
class CheckResult:
    check: str
    passed: bool
    details: str


REQUIRED_COLUMNS = {
    "account.csv": {"account_id", "account_number", "account_name", "account_type", "is_inactive", "last_modified_at"},
    "subsidiary.csv": {"subsidiary_id", "subsidiary_name", "base_currency_id", "is_inactive", "last_modified_at"},
    "department.csv": {"department_id", "department_name", "is_inactive", "last_modified_at"},
    "class.csv": {"class_id", "class_name", "is_inactive", "last_modified_at"},
    "accounting_period.csv": {"accounting_period_id", "period_name", "start_date", "end_date", "is_closed", "last_modified_at"},
    "currency.csv": {"currency_id", "currency_code", "currency_name", "last_modified_at"},
    "transaction_header.csv": {"transaction_id", "transaction_number", "transaction_type", "transaction_date", "posting_period_id", "subsidiary_id", "currency_id", "exchange_rate", "posting_flag", "memo", "last_modified_at"},
    "transaction_line.csv": {"transaction_id", "line_id", "account_id", "subsidiary_id", "department_id", "class_id", "currency_id", "debit_amount", "credit_amount", "foreign_amount", "line_memo", "last_modified_at"},
}


def load_frames(data_dir: Path) -> dict[str, pd.DataFrame]:
    frames = {}
    for filename in REQUIRED_COLUMNS:
        path = data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing required extract: {path}")
        frames[filename] = pd.read_csv(path)
    return frames


def schema_checks(frames: dict[str, pd.DataFrame]) -> list[CheckResult]:
    results = []
    for filename, required in REQUIRED_COLUMNS.items():
        missing = required - set(frames[filename].columns)
        results.append(CheckResult(
            f"schema:{filename}",
            not missing,
            "ok" if not missing else f"missing columns: {sorted(missing)}",
        ))
    return results


def duplicate_line_check(lines: pd.DataFrame) -> CheckResult:
    dupes = lines.duplicated(["transaction_id", "line_id"], keep=False)
    count = int(dupes.sum())
    return CheckResult("unique transaction-line key", count == 0, f"duplicate rows={count}")


def fk_check(child: pd.Series, parent: pd.Series, label: str, allow_null: bool = False) -> CheckResult:
    values = child.dropna() if allow_null else child
    missing = sorted(set(values.astype(str)) - set(parent.dropna().astype(str)))
    return CheckResult(label, not missing, f"missing references={missing[:10]}")


def journal_balance_check(headers: pd.DataFrame, lines: pd.DataFrame) -> CheckResult:
    journals = headers.loc[headers["transaction_type"].eq("JOURNAL"), "transaction_id"]
    x = lines[lines["transaction_id"].isin(journals)].copy()
    grouped = x.groupby("transaction_id", as_index=False).agg(
        debit=("debit_amount", "sum"), credit=("credit_amount", "sum")
    )
    grouped["difference"] = (grouped["debit"] - grouped["credit"]).round(2)
    bad = grouped[grouped["difference"].abs() > 0.01]
    return CheckResult("journal debit-credit balance", bad.empty, f"unbalanced journals={bad['transaction_id'].tolist()}")


def posting_period_check(headers: pd.DataFrame, periods: pd.DataFrame) -> CheckResult:
    h = headers.copy()
    p = periods.copy()
    h["transaction_date"] = pd.to_datetime(h["transaction_date"])
    p["start_date"] = pd.to_datetime(p["start_date"])
    p["end_date"] = pd.to_datetime(p["end_date"])
    merged = h.merge(p[["accounting_period_id", "start_date", "end_date"]], left_on="posting_period_id", right_on="accounting_period_id", how="left")
    bad = merged[(merged["transaction_date"] < merged["start_date"]) | (merged["transaction_date"] > merged["end_date"])]
    return CheckResult("posting-period date alignment", bad.empty, f"mismatched transactions={bad['transaction_id'].tolist()}")


def run_checks(frames: dict[str, pd.DataFrame]) -> list[CheckResult]:
    h = frames["transaction_header.csv"]
    l = frames["transaction_line.csv"]
    a = frames["account.csv"]
    s = frames["subsidiary.csv"]
    d = frames["department.csv"]
    c = frames["class.csv"]
    p = frames["accounting_period.csv"]
    cur = frames["currency.csv"]

    results = schema_checks(frames)
    results += [
        duplicate_line_check(l),
        fk_check(l["transaction_id"], h["transaction_id"], "line -> transaction header"),
        fk_check(l["account_id"], a["account_id"], "line -> account"),
        fk_check(l["subsidiary_id"], s["subsidiary_id"], "line -> subsidiary"),
        fk_check(l["department_id"], d["department_id"], "line -> department", allow_null=True),
        fk_check(l["class_id"], c["class_id"], "line -> class", allow_null=True),
        fk_check(h["posting_period_id"], p["accounting_period_id"], "header -> accounting period"),
        fk_check(h["currency_id"], cur["currency_id"], "header -> currency"),
        journal_balance_check(h, l),
        posting_period_check(h, p),
    ]
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data/sample"))
    args = parser.parse_args()

    frames = load_frames(args.data_dir)
    results = run_checks(frames)
    for r in results:
        print(f"{'PASS' if r.passed else 'FAIL'} | {r.check} | {r.details}")

    failed = [r for r in results if not r.passed]
    print(f"\nSummary: {len(results)-len(failed)}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
