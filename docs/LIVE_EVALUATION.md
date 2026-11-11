# Live evaluation evidence

Reviewed November 11, 2026. Four user-supplied exports from the deployed application. These are live model outputs, separate from the 24 passing fixture-based software tests. All four runs returned an answer and passed the application's model grounding check. AI-assisted review identified remaining quality failures; human sign-off is pending.

| Run | Plan | Version | Retrieval | Seconds | Wrong-vendor chunks | AI-assisted quality review |
|---|---|---|---|---:|---:|---|
| Initial baseline | Business | Pre-2.1; version not recorded | Baseline | 10.59 | 2 of 6 | Fail: Claude behavior/plan evidence applied to ChatGPT |
| Initial filtered | Business | Pre-2.1; version not recorded | Filtered | 9.80 | 0 of 6 | Fail: unsupported plan/control claims and problematic rollback |
| Later Personal run | Personal | 2.1-vendor-grounding | Filtered | 9.68 | 0 of 6 | Fail: citation gaps; different plan prevents controlled comparison |
| Business rerun | Business | 2.1-vendor-grounding | Filtered | 9.58 | 0 of 6 | Fail: wrong passage for one definition, unsupported scope statement in risks, instruction-like control text |

## What improved

The three Business runs have the same question and substantively identical scenario fields; permission whitespace differs. Filtered retrieval excluded Claude documentation in these observations. The updated Business run omitted speculative plan recommendations and marked console locations unknown. These observations do not establish general accuracy or statistically reliable latency gains.

## Remaining defects in the latest Business run

1. Fact 5 cites MS-REVIEW-2 for delegated-access semantics, while the specific definition is in MS-PERM-1.
2. The risk section describes Sites.Read.All without its definition in the retrieved notes.
3. Control locations contain instruction-like text such as “Never guess a path or role.”
4. Exact implementation settings and plan capabilities are still unknown, so the checklist is not ready for provisioning.

## Evidence files

- [Initial filtered Business](../evals/submission_evidence/01_initial_filtered_business.json)
- [Initial baseline Business](../evals/submission_evidence/02_initial_baseline_business.json)
- [Updated Personal](../evals/submission_evidence/03_v21_filtered_personal.json)
- [Updated Business](../evals/submission_evidence/04_v21_filtered_business.json)

The original question asks for risks, service-desk controls, the distinction between administrator consent and role assignment, citations and unknowns. Scenario: ChatGPT, Microsoft 365, live SharePoint access, delegated Files.Read.All and Sites.Read.All, confidential/personal sensitivity, and unknown permissions-review/consent-authority status.

## Method and limits

Review compares claims to the exact embedded evidence, checks vendor applicability and inspects controls, plan guidance and unknowns. Source IDs existing in retrieval is not semantic support. Original web pages were not independently revalidated for this review. No predeclared gold source set exists for this exact broad question, so source recall is not scored. Two original runs have no model/version/time metadata; later runs record model, version, time and corpus hash. The full 24-case/48-run planned suite remains unexecuted. The Excel workbook records the initial pair as E25; this report adds both later exports without overwriting the originals.

Next: expand the evidence library with permission definitions and configuration guides, tighten claim-level verification, remove instruction wording, then rerun the same scenarios and add vendor/boundary tests. Record failures and withheld answers rather than relabelling them as successful assessments.
