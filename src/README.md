# Source Code

This directory contains the Python components for the NetSuite-to-Snowflake financial reporting integration.

- `generate_sample_data.py` creates representative sample extracts for local validation and CI.
- `validate_extracts.py` performs schema and data-quality checks.
- `load_to_snowflake.py` contains the Snowflake loading workflow.

The repository CI validates these components on every push.
