# Week 2 demo script — target 4 minutes 40 seconds
Keep the app, docs/LIVE_EVALUATION.md and GitHub open in separate tabs. Sign in before recording. Never show Streamlit Secrets, API keys, billing or the password. Use generic data only. Record the live response as it happens; do not present an earlier JSON as a new run. If the response abstains, explain the safeguard honestly.

## 0:00–0:35 — Problem and goal
SHOW: application title and sidebar.
SAY: “I’m Aditi Jalota. I built an AI Integration Security Advisor for MSPs. Business users often request access for ChatGPT or Claude without knowing what permissions they are granting. My application helps explain those risks and prepares a service-desk review draft. It supports three bounded scenarios: ChatGPT with SharePoint, Claude with Microsoft 365, and the Gemini app with Google Workspace. It does not inspect or modify a customer tenant.”

## 0:35–1:10 — Explain the RAG pipeline
SHOW: Evidence library; expand one note and its source link.
SAY: “The evidence library contains nine short, paraphrased notes from official documentation. LangChain splits them into chunks and OpenAI creates embeddings. When a question arrives, filtered retrieval selects relevant vendor and platform evidence. LangGraph coordinates validation, retrieval, generation and verification. The model uses that evidence to produce structured advice with citations. These are curated notes, not complete vendor manuals.”

## 1:10–2:20 — Demonstrate live assessment
SHOW: pipeline version 2.1-vendor-grounding. Set ChatGPT; Business; Live SharePoint access; Delegated Files.Read.All and Sites.Read.All; Confidential / personal; both review/authority fields Unknown. Leave evaluation experiment unchecked.
TYPE: “What risks should we review before granting this access, and what controls should our service desk implement? Explain whether administrator consent gives ChatGPT an administrator role. Cite your sources and identify any missing information.”
CLICK: Assess with evidence. While it runs, explain the selected context.
SAY: “This is a real model call. I’m asking about delegated access and keeping approval status unknown. I want the answer to distinguish administrator consent from giving the application an administrator role.”
SHOW: result, facts, risks and unknowns; expand Retrieved evidence and workflow.
SAY IF ANSWER: “The output separates documented claims, inferred risks and proposed controls. Unknown settings remain visible. This result still requires review; a successful model check is not proof that every claim is supported.”
SAY IF ABSTAIN: “The evidence check withheld this answer. That is a valid safeguard outcome. The retrieved sources remain inspectable, and I can narrow the question or improve the evidence library.”
DOWNLOAD: assessment JSON.

## 2:20–2:50 — Service desk handoff
SHOW: if a filtered answer exists, acknowledge reviewing risks and download the ticket. Open it only if time allows.
SAY: “Acknowledging risk review enables a draft ticket. It includes the request, risks, proposed checks and unresolved questions. The ticket says authorization pending. It does not send anything to a help desk or provision access.”
IF NO ANSWER: show advisor/ticket.py or explain the intended export, saying “This run was withheld, so no ticket is generated.” Do not imply a live ticket test succeeded.

## 2:50–3:45 — Show evaluation and iteration
SHOW: docs/LIVE_EVALUATION.md in GitHub.
SAY: “I compared the same Business-plan question using baseline and filtered retrieval. Baseline retrieved two Claude passages for a ChatGPT question, and the answer incorrectly reused them. Filtered retrieval returned no Claude passages. Both automated grounding checks initially passed, but review still found unsupported claims.
“I then added deterministic vendor checks, separated the baseline experiment, and tightened plan and setting instructions. A later Business-plan run avoided the wrong-vendor sources and speculative plan recommendations. It still had a citation mismatch and an unsupported scope explanation. I recorded that as a remaining failure, not a pass. Four live exports were reviewed; one used a different Personal plan and is not a controlled comparison.”

## 3:45–4:15 — Boundary test
SHOW: change intended plan to Unknown and submit the same question.
SAY: “With the subscription unknown, the app asks for clarification instead of proceeding.”
If the actual result differs, describe it as a new finding. Do not claim a test passed without observing it.

## 4:15–4:40 — AI coding tools and lessons
SHOW: GitHub repository, tests and project documentation.
SAY: “I used Codex to help implement the application, prompts, tests and deployment fixes. Twenty-four software tests pass, but those use fixtures and are separate from factual AI evaluation. My main learning is that valid citation IDs do not guarantee supported claims. The next improvement is richer configuration documentation and stricter claim-level checks. This is a live learning prototype, not a production security approval system.”

## Submission checklist
- Submit the Google Doc link for project documentation.
- Record and upload this walkthrough, no longer than five minutes, and submit its viewable URL.
- Submit https://github.com/Aditijalota/AgenticApplicatication-MSP for project assets.
- Verify reviewer access to the Google Doc and video.
- Optional: add the actual deployed Streamlit URL from the browser. Do not publish its password.
