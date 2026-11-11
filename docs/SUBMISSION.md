# Week 2 project: AI Integration Security Advisor

## Problem and users
Business users request AI access without understanding permission scope. MSP service desks need a documented risk explanation and implementable controls before provisioning. This advisor covers ChatGPT live SharePoint, Claude Microsoft 365, and Gemini app with Google Workspace.

## Workflow
Collect vendor, platform, subscription, connection method, sensitivity, permission details and consent context. Retrieve attributed vendor/platform evidence. Generate cited facts, conditional business risks, plan guidance, proposed controls and unknowns. Check citations and grounding. After risk review, export a ticket containing scope, prerequisites, setting locations when documented, owners, verification, rollback and unresolved approvals.

## Data and implementation
Nine curated, paraphrased official-source notes with provenance metadata; LangChain cleaning/chunking and vector retrieval; OpenAI embeddings and structured generation; LangGraph bounded routing; Streamlit interface. Tenant access and automatic execution are excluded. LlamaCloud and Pinecone are not wired into this build.

## Iterations
Initial scope covered ChatGPT live SharePoint. Expanded to three vendor-specific scenarios and service-desk tickets. Added metadata filtering to reduce cross-vendor/method contamination. Added evidence validation for controls and plan recommendations. Keep user risk acknowledgement separate from authorization.

## Evaluation
21 test cases in evals/cases.json, baseline versus filtered retrieval. Fixture-based software tests do not measure live model quality. Run evaluate.py with a privately configured API key, retain real outputs, and record failures and human judgments here. Live model metrics and deployment URL are pending; do not invent them.

## Critical limitations
Small curated corpus; limited Gemini settings detail; no tenant inspection; model-based grounding can miss errors; exact requested scopes and license/control availability require human verification. Production needs identity management, durable quotas, formal review/audit records, ongoing source refresh and broader adversarial evaluations.
