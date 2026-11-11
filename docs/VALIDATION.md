# Validation — 2026-11-11

Executed against the expanded three-vendor build in Python 3.12:

- `python -m pytest -q`: **17 passed**.
- Python compilation: passed.
- Tests cover scope guards, vendor/platform evidence isolation, citation rejection, withholding failed grounding, empty retrieval, private setup/login screens, and ticket review/authorization boundaries.

LLM and embedding calls in workflow tests are fixtures. No live API evaluation, live factual-quality score or completed public deployment is claimed. Streamlit Community Cloud was inspected and requires user sign-in. The current 21-case evaluation set remains unexecuted against a live model.

Manual release checks still required after configuring private host secrets: sign in to app, obtain an actual cited assessment, inspect controls against linked sources, acknowledge risks, download ticket, verify unknown scope/license details remain blockers, and run baseline/filtered evaluation.
