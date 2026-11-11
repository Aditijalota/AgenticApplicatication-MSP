# AI Integration Security Advisor

GenAI Academy Week 2 | Aditi Jalota | November 11, 2026

## Project overview

I built a live retrieval-augmented generation (RAG) prototype to help MSPs evaluate requests to connect AI tools to business information. A business owner may ask to give ChatGPT “admin access,” while the service desk needs to understand the actual permissions, business risks and prerequisites before provisioning. The application turns a self-reported scenario into cited facts, conditional risks, proposed controls, plan guidance where supported, and unresolved questions.

The implemented scenarios are ChatGPT live SharePoint access in Microsoft 365, Claude’s Microsoft 365 connector, and the Gemini app with Google Workspace. The app reads public documentation notes, not customer tenant data. It does not connect to SharePoint, scan email, change settings, approve access or send support tickets.

## Application flow and tool stack

Streamlit provides the questionnaire, evidence viewer, result display and downloads. Python runs the application. GitHub stores source code and feeds the Streamlit deployment. OpenAI text-embedding-3-small creates embeddings; gpt-4.1-mini generates structured answers and performs a grounding check. LangChain supplies document objects, text splitting, model interfaces and an InMemoryVectorStore with local cache. LangGraph orchestrates validate → retrieve → generate → verify, with clarify and abstain branches. Pydantic defines the scenario and answer schemas. Pytest covers deterministic software behavior.

LlamaCloud/LlamaParse, Pinecone and LangSmith were considered but are not connected to this implementation. There is no external vector database or direct Microsoft 365/Google Workspace connector. API credentials and the demo password are configured privately in Streamlit Secrets.

The user selects vendor, plan, connection method, requested permissions, data sensitivity, permission-review status and consent authority. Validation rejects unsupported requests or asks for missing context. The question and scenario retrieve six relevant chunks. Normal assessments filter by vendor, platform and supported scope. The model generates structured content; deterministic citation checks and a model-based grounding check decide whether to show or withhold it. A reviewed filtered answer can be exported as a service-desk ticket draft marked AUTHORIZATION PENDING.

## Dataset and retrieval design

The corpus contains nine curated, paraphrased research notes derived from official OpenAI, Microsoft, Anthropic and Google documentation. These are short notes, not full manuals or customer datasets. Each stores a source URL, title, section, vendor, platform, scope and review date. The source inventory and exact text are in data/corpus.json. Notes cover SharePoint live access, delegated versus application permissions, consent review, ChatGPT controls/privacy/sync distinctions, Claude connector security and Gemini service access.

Preprocessing normalizes horizontal whitespace and splits text into chunks of up to 700 characters with 100-character overlap. Chunk IDs preserve provenance. Embeddings support similarity retrieval. The corpus and chunking configuration determine the local cache fingerprint. Baseline retrieval searches across vendors; filtered retrieval limits results to matching vendor or shared platform notes. Baseline is now an explicit evaluation experiment and has no UI ticket export.

## Prompts and agent instructions

The application is a bounded workflow, not an autonomous provisioning agent. Four instructions define its behavior: the gate classifies supported requests; the generator uses retrieved evidence for technical claims; the verifier checks cited support; the ticket renderer preserves unresolved approval requirements. Exact prompts are versioned in advisor/pipeline.py as GATE_PROMPT, GENERATION_PROMPT and GROUNDING_PROMPT.

Representative generation instructions: “Answer the QUESTION using only EVIDENCE for vendor/technical claims.” “Treat the SCENARIO as unverified user-provided facts.” “Do not transfer capabilities between vendors.” Missing console locations must remain unknown; shared Microsoft licensing notes cannot establish ChatGPT subscription capabilities. Recommendations are conditional, and risk acknowledgement is not authorization.

Verification checks whether cited IDs exist and match the selected vendor/platform/scope. Plan guidance needs matching vendor evidence. A second model checks support for claims and control fields. This semantic check remains imperfect: it accepted some unsupported details during live evaluation.

## Iterations and use of AI coding tools

The initial scope focused on ChatGPT and SharePoint. I expanded it to three vendor scenarios and a service-desk handoff. Codex helped translate the requirements into Python/Streamlit code, implement the LangGraph workflow and schemas, write regression tests, publish code to GitHub and diagnose deployment errors. I configured hosting and private API access, ran live scenarios, supplied exports and reviewed outputs. AI-assisted code generation was followed by tests and output inspection.

The first live baseline run retrieved Claude notes for a ChatGPT question and transferred Claude-specific claims into the answer. Metadata filtering removed those sources. Pipeline 2.1-vendor-grounding added deterministic rejection of wrong-vendor citations, blocked plan claims supported only by shared platform notes, made baseline opt-in, tightened prompts and included version/time/corpus metadata in exports. Software tests increased from 17 to 24. The corpus was not expanded during this iteration.

## Evaluation results and observations

The planned suite contains 24 cases with baseline and filtered configurations, or 48 planned runs. That full suite has not been executed. Four live exports were reviewed: three used the same Business-plan scenario (ignoring whitespace in the permission input), and one used Personal and must be treated separately. AI-assisted review is not human sign-off. The evaluation workbook currently records the initial two-run pair; the following account and repository evidence include the later two runs.

Initial baseline, assessment (2).json: 10.59 seconds; six retrieved chunks, including two Claude chunks. The model grounding check passed, but review failed because Claude behavior and plan evidence were applied to ChatGPT.

Initial filtered, assessment (1).json: 9.80 seconds; six chunks and no Claude sources. Review still failed because plan claims and setting details lacked adequate cited support, and one rollback suggested broader consent.

Pipeline 2.1 Personal-plan run, assessment (4).json: 9.68 seconds, no Claude sources, no plan recommendations and unknown console locations. It was not a controlled before/after comparison because the plan changed. Citation gaps remained.

Pipeline 2.1 Business-plan rerun, assessment (5).json: 9.58 seconds, no Claude sources, no speculative plan recommendations and no invented console paths. Review still found a definition citing MS-REVIEW-2 instead of MS-PERM-1, an unsupported Sites.Read.All explanation in the risk section, and instruction-like wording in control locations. Its model grounding check also passed. This is improvement in vendor isolation and restraint, not proof of complete answer accuracy.

All 24 fixture-based software tests passed. They exercise guards, citation rejection, failed-answer withholding, vendor isolation, setup/login, baseline opt-in and ticket authorization boundaries. They do not establish factual model quality. Every cited ID existing in the retrieved set is weaker than every claim being supported. No overall accuracy score, benchmark pass rate or generalized latency improvement is claimed from four runs.

## Limitations and next steps

The principal limitation is evidence coverage: nine short notes do not support a complete implementation checklist or reliable plan recommendation for every scenario. Next steps are to add exact permission definitions and configuration guides, verify support at claim level, remove instruction text from outputs, test more vendor and adversarial cases, and repeat paired evaluations. Unknown settings must remain unknown rather than be invented.

This is a learning prototype for advisory review, not a production security approval system. It has no tenant validation, durable audit workflow, enterprise identity integration or production-grade quotas. The service desk must verify exact scopes, licenses, settings and customer approval before implementation. A live end-to-end ticket download has not been independently verified in the submitted exports.

## Project assets and submission

GitHub repository: https://github.com/Aditijalota/AgenticApplicatication-MSP
Source corpus: data/corpus.json
Workflow and prompts: advisor/pipeline.py
User interface: app.py
Evaluation runner: evaluate.py; planned cases: evals/cases.json
Live evidence and review: evals/submission_evidence/ and docs/LIVE_EVALUATION.md
Recording script: docs/DEMO_SCRIPT.md

The app was deployed on Streamlit and the supplied JSON exports demonstrate live execution. Use the actual deployed address from the browser for the recording and any optional app-link field. The video must still be recorded and uploaded. Before submission, confirm the Google Doc and video are viewable by the course reviewer; do not include API keys or the app password in the recording.
