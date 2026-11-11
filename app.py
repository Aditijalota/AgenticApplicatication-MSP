import hashlib
import hmac
import json
import os
import time

import streamlit as st

from advisor.ticket import render_ticket
from advisor.pipeline import CORPUS, MODEL, PIPELINE_VERSION, Scenario, create_graph, input_guard, run

st.set_page_config(page_title='AI Integration Security Advisor', page_icon='🛡️', layout='wide')


def secret(name, default=''):
    try:
        return os.getenv(name) or st.secrets.get(name, default)
    except FileNotFoundError:
        return os.getenv(name, default)


def safe_error_message(exc):
    # Never expose exception text, response bodies, headers, or credentials.
    from openai import (AuthenticationError, PermissionDeniedError, RateLimitError,
                        NotFoundError, BadRequestError, APIConnectionError, APITimeoutError)
    if isinstance(exc, AuthenticationError):
        return 'API authentication failed (401). Replace OPENAI_API_KEY in Streamlit Secrets with an active OpenAI API key.'
    if isinstance(exc, PermissionDeniedError):
        return 'API permission denied (403). Check that the key and project permit the selected chat model and embeddings.'
    if isinstance(exc, RateLimitError):
        if getattr(exc, 'code', None) in ('insufficient_quota', 'credit_balance_exhausted'):
            return 'API credits or quota exhausted. Check billing and available credits for the OpenAI organization that owns this key.'
        return 'API rate or quota limit reached (429). Check OpenAI billing and project limits; if funded, wait a minute and retry.'
    if isinstance(exc, NotFoundError):
        return 'API model or resource unavailable (404). Check project access to OPENAI_MODEL and text-embedding-3-small.'
    if isinstance(exc, BadRequestError):
        return 'API rejected the request (400). Model configuration or the structured response schema needs investigation.'
    if isinstance(exc, APITimeoutError):
        return 'The AI request timed out. Retry once; persistent failures require checking provider availability.'
    if isinstance(exc, APIConnectionError):
        return 'Could not connect to the AI provider. Retry once and check network/provider availability.'
    # Class names identify software failures without exposing user inputs.
    name = type(exc).__name__
    safe_name = name if name.isidentifier() and len(name) < 80 else 'InternalError'
    return 'Application processing failed (' + safe_name + '). Report this error category for debugging.'


st.title('AI Integration Security Advisor')
st.caption('MSP decision support · ChatGPT · Claude · Gemini · Week 2 RAG prototype')
st.caption('Pipeline ' + PIPELINE_VERSION)

# Default closed: requires a password unless the operator explicitly enables local mode.
password = secret('APP_PASSWORD')
local_mode = str(secret('LOCAL_DEMO', 'false')).lower() == 'true'
if not password and not local_mode:
    st.info('Setup required: configure APP_PASSWORD and OPENAI_API_KEY in server secrets. See README.')
    st.stop()
if password and not st.session_state.get('authenticated'):
    with st.form('login'):
        entered = st.text_input('Demo access password', type='password')
        submit_login = st.form_submit_button('Open advisor')
    if submit_login:
        if hmac.compare_digest(entered, password):
            st.session_state.authenticated = True
            st.rerun()
        st.error('Incorrect password.')
    st.stop()

st.info('This advisor uses public documentation notes and your answers. It does not inspect or modify a tenant. Use generic scenarios; do not enter client files, credentials or personal identifiers.')
api_key = secret('OPENAI_API_KEY')
model = secret('OPENAI_MODEL', MODEL)
with st.sidebar:
    st.header('Assessment context')
    vendor = st.selectbox('AI vendor', ['ChatGPT', 'Claude', 'Gemini'])
    platform = 'Google Workspace' if vendor == 'Gemini' else 'Microsoft 365'
    st.caption('Supported platform: ' + platform)
    plan = st.text_input('Current or intended plan', value='Unknown', max_chars=100)
    methods = {'ChatGPT': 'Live SharePoint access', 'Claude': 'Microsoft 365 connector', 'Gemini': 'Gemini app with Workspace'}
    method = st.selectbox('Connection method', ['Unknown', methods[vendor]])
    permissions = st.text_input('Requested scopes / access type (no secrets)', max_chars=1500,
                                help='For example: delegated Mail.Read. If unknown, the assessment must identify this as a blocker.')
    sensitivity = st.selectbox('Data sensitivity', ['Unknown', 'Public', 'Internal', 'Confidential / personal'])
    reviewed = st.selectbox('Source permissions reviewed?', ['Unknown', 'Yes', 'No'])
    authorized = st.selectbox('Administrator consent authority confirmed?', ['Unknown', 'Yes', 'No'])
    experiment = st.checkbox('Enable evaluation experiment', value=False)
    mode = st.selectbox('Retrieval experiment', ['filtered', 'baseline']) if experiment else 'filtered'
    if mode == 'baseline':
        st.warning('Evaluation only: baseline searches all vendors. Wrong-vendor citations will be rejected. Ticket export is disabled.')
    else:
        st.caption('Vendor and platform filtering enabled.')
    st.caption('Corpus reviewed: November 9–11, 2026. Product behavior may change. Verify linked originals before implementation.')

tab, sources_tab, eval_tab = st.tabs(['Ask the advisor', 'Evidence library', 'Evaluation guide'])
with sources_tab:
    records = json.loads(CORPUS.read_text())
    st.write(f'{len(records)} curated research notes from official sources. These are paraphrases, not full documents.')
    for item in records:
        with st.expander(item['title']):
            st.write(item['text'])
            st.caption(f"Scope: {item['scope']} · Section: {item['section']} · Reviewed: {item['reviewed']}")
            st.link_button('Open original documentation', item['url'])
with eval_tab:
    st.write('Run python evaluate.py --mode both after setting the API key. Review each generated answer against the reference outcome in the Excel workbook.')
    st.write('Automated measures: expected route match, expected source recall, citation ID validity and latency. Human measures: correctness, faithfulness, useful controls and appropriate uncertainty.')
    st.warning('Passing citation-ID validation or a model grounding check does not prove correctness. Live evaluation results are not available until the model calls are run.')
with tab:
    st.markdown('**Try:** Does administrator consent make ChatGPT a Global Administrator?')
    with st.form('question'):
        question = st.text_area('What do you need to assess?', max_chars=1500, height=110,
                                placeholder='Can our MSP enable ChatGPT to summarize SharePoint documents containing employee information?')
        submitted = st.form_submit_button('Assess with evidence', type='primary')
    if submitted:
        st.session_state.pop('result', None)
        st.session_state.risk_reviewed = False
        scenario = Scenario(vendor=vendor, platform=platform, requested_permissions=permissions, plan=plan, method=method, sensitivity=sensitivity,
                            permissions_reviewed=reviewed, consent_authorized=authorized)
        guard = input_guard(question, scenario.model_dump())
        if guard:
            st.session_state.result = {'route': guard.route, 'message': guard.message, 'assessment': None,
                                       'evidence': [], 'trace': ['input guard: ' + guard.route], 'latency_seconds': 0, 'configuration': mode}
        elif not api_key:
            st.error('OpenAI API access is not configured. Add OPENAI_API_KEY to server secrets; never paste it into a question.')
        elif st.session_state.get('queries', 0) >= 30:
            st.warning('This demo session has reached its 30-request limit.')
        elif time.time() - st.session_state.get('last_query', 0) < 5:
            st.warning('Please wait five seconds between requests.')
        else:
            st.session_state.queries = st.session_state.get('queries', 0) + 1
            st.session_state.last_query = time.time()
            # Per-session graph prevents scenario state or user results being shared across users.
            signature = hashlib.sha256((api_key + model + PIPELINE_VERSION).encode()).hexdigest()
            try:
                with st.spinner('Retrieving evidence and checking the assessment…'):
                    if st.session_state.get('graph_signature') != signature:
                        st.session_state.graph = create_graph(api_key, model)
                        st.session_state.graph_signature = signature
                    st.session_state.result = run(st.session_state.graph, question, scenario, mode)
                    st.session_state.result['model'] = model
            except Exception as exc:
                st.session_state.pop('result', None)
                st.error(safe_error_message(exc))
                st.caption('No assessment was completed. Credentials and raw provider responses remain hidden.')
    result = st.session_state.get('result')
    if result:
        st.subheader({'answer': 'Evidence-based assessment', 'clarify': 'More information needed', 'abstain': 'Unable to conclude'}[result['route']])
        if result['message']:
            st.write(result['message'])
        if result['assessment']:
            a = result['assessment']
            st.caption('Based on your self-reported context. Verify configuration before implementation.')
            st.markdown('**Documented facts**')
            for fact in a['facts']:
                st.write(f"• {fact['text']} [{', '.join(fact['citations'])}]")
            st.markdown('**Conditional business risks**')
            for item in a.get('risks', []):
                st.write('• ' + item)
            st.markdown('**Plan guidance**')
            for item in a.get('plan_guidance', []):
                st.write(f"{item['text']} [{', '.join(item['citations'])}]")
            st.markdown('**Proposed controls for the service desk**')
            for c in a.get('controls', []):
                with st.expander(c['action']):
                    for field in ['location', 'prerequisites', 'owner', 'verification', 'rollback']:
                        st.write(f"{field.title()}: {c[field]}")
                    st.caption('Evidence: ' + ', '.join(c['citations']))
            st.markdown('**Advisory recommendations**')
            for item in a['recommendations']:
                st.write('• ' + item)
            st.markdown('**What still needs verification**')
            for item in a['unknowns']:
                st.write('• ' + item)
            reviewed_risks = st.checkbox('I have reviewed these risks and unknowns. This is not authorization to provision.', key='risk_reviewed')
            if reviewed_risks and result['configuration'] != 'baseline':
                ticket = render_ticket(result, reviewed=True)
                st.download_button('Download service-desk ticket draft', ticket, 'service-desk-ticket.md', 'text/markdown')
                st.caption('This ticket uses the submitted assessment context, not subsequent changes in the sidebar.')
            elif reviewed_risks:
                st.info('Baseline is for evaluation only. Run a filtered assessment before creating a service-desk ticket.')
        with st.expander('Retrieved evidence and workflow'):
            st.caption(f"{result['configuration']} · {result['latency_seconds']} seconds")
            st.write(' → '.join(result['trace']))
            for d in result['evidence']:
                st.markdown(f"**{d['chunk_id']} · {d['title']}**")
                st.write(d['text'])
                st.link_button('Verify original source', d['url'], key='source-' + d['chunk_id'])
        st.download_button('Download this assessment', json.dumps(result, indent=2), 'assessment.json', 'application/json')
