from __future__ import annotations

import argparse
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

TABLE_MAP = {
    "account.csv": "ACCOUNT",
    "subsidiary.csv": "SUBSIDIARY",
    "department.csv": "DEPARTMENT",
    "class.csv": "CLASS",
    "accounting_period.csv": "ACCOUNTING_PERIOD",
    "currency.csv": "CURRENCY",
    "transaction_header.csv": "TRANSACTION_HEADER",
    "transaction_line.csv": "TRANSACTION_LINE",
}


def connection():
    load_dotenv()
    required = [
        "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing Snowflake environment variables: {missing}")

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        role=os.getenv("SNOWFLAKE_ROLE") or None,
    )


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [c.upper() for c in out.columns]
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data/sample"))
    args = parser.parse_args()

    with connection() as conn:
        for filename, table in TABLE_MAP.items():
            path = args.data_dir / filename
            df = normalize_columns(pd.read_csv(path))
            success, nchunks, nrows, _ = write_pandas(
                conn,
                df,
                table_name=table,
                database=os.environ["SNOWFLAKE_DATABASE"],
                schema=os.environ["SNOWFLAKE_SCHEMA"],
                auto_create_table=False,
                overwrite=False,
            )
            print(f"{filename} -> {table}: success={success}, chunks={nchunks}, rows={nrows}")


if __name__ == "__main__":
    main()
