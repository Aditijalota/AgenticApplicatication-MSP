# Validation — 2026-11-11

Executed against pipeline 2.1-vendor-grounding in Python 3.12:

- `python -m pytest -q`: **24 passed**.
- Python compilation: passed.
- Tests cover scope guards, vendor/platform evidence isolation, citation rejection, withholding failed grounding, empty retrieval, private setup/login screens, and ticket review/authorization boundaries.

LLM and embedding calls in software tests are fixtures. The user deployed on Streamlit and supplied two actual assessment exports for one identical ChatGPT scenario. These pre-fix runs are separate from the 24 planned cases (48 runs), which remain unexecuted. The workbook records the live pair as E25.

## Observed pre-fix live pair

Baseline: 10.59 seconds, 6 chunks, including 2 Claude chunks. Filtered: 9.80 seconds, 6 chunks, no Claude chunks. Both model grounding checks passed. AI-assisted review failed both for unsupported claims: baseline transferred Claude behavior and plan evidence to ChatGPT; filtered still used shared Microsoft licensing evidence for a ChatGPT Business claim and guessed control details. Human sign-off remains pending. One pair cannot establish general accuracy or speed improvement.

## Changes driven by evaluation

- Normal UI assessments always use filtered retrieval. Baseline is an opt-in evaluation experiment with no UI ticket export.
- Deterministic citation checks reject wrong vendor/platform/scope sources even if the model checker would accept them.
- Shared platform documentation alone cannot support AI vendor plan guidance.
- Filtered retrieval independently removes mismatched results returned by a vector store.
- Prompts require unknown setting paths and prerequisites to remain unknown, separate Microsoft licensing from AI subscriptions, and prohibit broader consent as rollback.
- Export metadata records pipeline version, corpus hash and completion time; UI exports also record the configured model.

Regression tests reproduce wrong-vendor citation acceptance, shared-only plan citations, and a store ignoring filters. These checks pass with fixtures; post-fix live answer quality has NOT yet been verified. Model-based semantic grounding remains fallible. Existing nine-note corpus has gaps and was not expanded in this change.

Next live checks: confirm version 2.1-vendor-grounding in the app, rerun the exact E25 scenario, inspect evidence and claims, test an unknown plan (clarify), Grok (abstain), and a supported Claude or Gemini scenario. On a supported filtered answer, acknowledge risks and download the ticket, verifying authorization remains pending. Record new runs without overwriting the pre-fix pair.
