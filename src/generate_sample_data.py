from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample"


def write(name: str, rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / name, index=False)


def main() -> None:
    ts = "2026-09-01 12:00:00"

    write("currency.csv", [
        {"currency_id": 1, "currency_code": "USD", "currency_name": "US Dollar", "last_modified_at": ts},
        {"currency_id": 2, "currency_code": "EUR", "currency_name": "Euro", "last_modified_at": ts},
    ])

    write("subsidiary.csv", [
        {"subsidiary_id": 10, "subsidiary_name": "US Operations", "base_currency_id": 1, "is_inactive": False, "last_modified_at": ts},
        {"subsidiary_id": 20, "subsidiary_name": "EU Operations", "base_currency_id": 2, "is_inactive": False, "last_modified_at": ts},
    ])

    write("account.csv", [
        {"account_id": 100, "account_number": "1000", "account_name": "Cash", "account_type": "ASSET", "is_inactive": False, "last_modified_at": ts},
        {"account_id": 200, "account_number": "2000", "account_name": "Accounts Payable", "account_type": "LIABILITY", "is_inactive": False, "last_modified_at": ts},
        {"account_id": 400, "account_number": "4000", "account_name": "Product Revenue", "account_type": "INCOME", "is_inactive": False, "last_modified_at": ts},
        {"account_id": 500, "account_number": "5000", "account_name": "Operating Expense", "account_type": "EXPENSE", "is_inactive": False, "last_modified_at": ts},
        {"account_id": 599, "account_number": "5999", "account_name": "Legacy Expense", "account_type": "EXPENSE", "is_inactive": True, "last_modified_at": ts},
    ])

    write("department.csv", [
        {"department_id": 1, "department_name": "Finance", "is_inactive": False, "last_modified_at": ts},
        {"department_id": 2, "department_name": "Operations", "is_inactive": False, "last_modified_at": ts},
    ])

    write("class.csv", [
        {"class_id": 1, "class_name": "Shared Services", "is_inactive": False, "last_modified_at": ts},
        {"class_id": 2, "class_name": "Core Product", "is_inactive": False, "last_modified_at": ts},
    ])

    write("accounting_period.csv", [
        {"accounting_period_id": 202601, "period_name": "Jan 2026", "start_date": "2026-01-01", "end_date": "2026-01-31", "is_closed": True, "last_modified_at": ts},
        {"accounting_period_id": 202602, "period_name": "Feb 2026", "start_date": "2026-02-01", "end_date": "2026-02-28", "is_closed": True, "last_modified_at": ts},
    ])

    write("transaction_header.csv", [
        {"transaction_id": 10001, "transaction_number": "JE10001", "transaction_type": "JOURNAL", "transaction_date": "2026-01-15", "posting_period_id": 202601, "subsidiary_id": 10, "currency_id": 1, "exchange_rate": 1.0, "posting_flag": True, "memo": "January accrual", "last_modified_at": "2026-01-15 18:00:00"},
        {"transaction_id": 10002, "transaction_number": "INV10002", "transaction_type": "INVOICE", "transaction_date": "2026-02-10", "posting_period_id": 202602, "subsidiary_id": 10, "currency_id": 1, "exchange_rate": 1.0, "posting_flag": True, "memo": "Customer invoice", "last_modified_at": "2026-02-10 18:00:00"},
        {"transaction_id": 10003, "transaction_number": "JE10003", "transaction_type": "JOURNAL", "transaction_date": "2026-02-20", "posting_period_id": 202602, "subsidiary_id": 20, "currency_id": 2, "exchange_rate": 1.0, "posting_flag": True, "memo": "EU operating entry", "last_modified_at": "2026-02-20 18:00:00"},
    ])

    write("transaction_line.csv", [
        {"transaction_id": 10001, "line_id": 1, "account_id": 500, "subsidiary_id": 10, "department_id": 1, "class_id": 1, "currency_id": 1, "debit_amount": 1000.00, "credit_amount": 0.00, "foreign_amount": 1000.00, "line_memo": "Accrued expense", "last_modified_at": "2026-01-15 18:00:00"},
        {"transaction_id": 10001, "line_id": 2, "account_id": 200, "subsidiary_id": 10, "department_id": 1, "class_id": 1, "currency_id": 1, "debit_amount": 0.00, "credit_amount": 1000.00, "foreign_amount": -1000.00, "line_memo": "Accrued liability", "last_modified_at": "2026-01-15 18:00:00"},
        {"transaction_id": 10002, "line_id": 1, "account_id": 100, "subsidiary_id": 10, "department_id": 2, "class_id": 2, "currency_id": 1, "debit_amount": 2500.00, "credit_amount": 0.00, "foreign_amount": 2500.00, "line_memo": "Receivable/cash side", "last_modified_at": "2026-02-10 18:00:00"},
        {"transaction_id": 10002, "line_id": 2, "account_id": 400, "subsidiary_id": 10, "department_id": 2, "class_id": 2, "currency_id": 1, "debit_amount": 0.00, "credit_amount": 2500.00, "foreign_amount": -2500.00, "line_memo": "Revenue side", "last_modified_at": "2026-02-10 18:00:00"},
        {"transaction_id": 10003, "line_id": 1, "account_id": 500, "subsidiary_id": 20, "department_id": 2, "class_id": 1, "currency_id": 2, "debit_amount": 900.00, "credit_amount": 0.00, "foreign_amount": 900.00, "line_memo": "EU expense", "last_modified_at": "2026-02-20 18:00:00"},
        {"transaction_id": 10003, "line_id": 2, "account_id": 100, "subsidiary_id": 20, "department_id": 2, "class_id": 1, "currency_id": 2, "debit_amount": 0.00, "credit_amount": 900.00, "foreign_amount": -900.00, "line_memo": "EU cash", "last_modified_at": "2026-02-20 18:00:00"},
    ])

    print(f"Generated sample extracts in {OUT}")


if __name__ == "__main__":
    main()
