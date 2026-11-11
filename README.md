# AI Integration Security Advisor for MSPs

This application addresses a business gap in the MSP world: translating AI integration requests into evidence-backed risk explanations and service-desk review tickets.

Business users describe proposed access. A RAG workflow retrieves curated official documentation, explains conditional risks, proposes controls and plan guidance, and produces a downloadable ticket after the user acknowledges reviewing the risks. Review is not permission to provision.

## Supported MVP scenarios

| Vendor | Platform | Method |
|---|---|---|
| ChatGPT | Microsoft 365 | Live SharePoint access |
| Claude | Microsoft 365 | Microsoft 365 connector |
| Gemini | Google Workspace | Gemini app / Workspace service context |

No tenant connection, document inspection, automatic provisioning or ticket submission. Other combinations and administrator-managed sync are outside this MVP. Gemini evidence is introductory: exact connected-app configuration may remain an explicit blocker.

## Stack and architecture

Python 3.12; Streamlit UI; LangChain documents, chunking and retrieval; OpenAI embeddings and configurable answer model; LangGraph validation → retrieval → generation → evidence verification; local persisted InMemoryVectorStore; pytest; GitHub source; Streamlit Community Cloud deployment target.

LlamaCloud/LlamaParse and Pinecone are possible later additions, **not connected in this version**. The small curated corpus currently uses attributed JSON research notes rather than PDF parsing. This avoids requiring additional keys for the deadline prototype.

Nine official-source research notes are cleaned and split into 700-character chunks with 100-character overlap. Each chunk retains URL, section, vendor, platform and review date. Retrieval compares unfiltered dense search with vendor/platform/method-filtered dense search (top 6). Embeddings use `text-embedding-3-small`; the default answer model is `gpt-4.1-mini`, configurable through `OPENAI_MODEL`.

Factual claims, controls and plan guidance require retrieved citation IDs. A separate model call checks grounding; unsupported answers are withheld. A model check is not a guarantee of correctness. Risks and recommendations are conditional inferences from self-reported context, not findings from inspected business data.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
# Privately edit secrets.toml with your API key and demo password.
streamlit run app.py
```

Never commit `.streamlit/secrets.toml`. Never paste API keys into questions or chat. Without a password (or explicit local-demo mode), the UI remains on its setup screen. This is a demonstration password gate, not production identity management. Session quotas can be reset by starting a new session; configure provider budgets separately.

## Deploy

1. Sign into [Streamlit Community Cloud](https://share.streamlit.io/).
2. Create an app from `Aditijalota/AgenticApplicatication-MSP`, branch `main`, entrypoint `app.py`.
3. Choose Python 3.12. In Advanced settings, set private `OPENAI_API_KEY` and `APP_PASSWORD` values. Keep `LOCAL_DEMO` false.
4. Deploy, open the generated URL, and test authentication plus a cited answer before sharing.

[Official deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Evaluation and limitations

```bash
python -m pytest -q
python evaluate.py --mode both
```

`evals/cases.json` is the current 21-case definition. Earlier delivered Excel workbooks cover the original 18-case ChatGPT scope and are not the current multivendor evaluation. The runner produces actual responses, source recall, route matching and latency. Manually review factual support, control usefulness, plan accuracy, missing permissions and ticket actionability. No live-model results are claimed until real calls run.

The corpus contains paraphrased notes, not complete downloaded vendor manuals. Claude/Gemini coverage is thinner than ChatGPT coverage. Exact OAuth scopes and permission type must be checked against the real consent screen. Unknown settings, license requirements, residual risks and authorization remain blockers. This prototype is advisory and is not production-ready security certification.

## Submission assets

`docs/SUBMISSION.md` provides the project narrative; `docs/DEMO_SCRIPT.md` provides a five-minute demo outline. Add measured results and the real deployment URL before final submission.
