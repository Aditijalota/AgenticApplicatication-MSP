import json

from advisor.pipeline import (Assessment, Gate, Grounding, ROOT, Scenario,
                              build_graph, citation_errors, input_guard, load_documents, run,
                              scope_errors, evidence_matches, PIPELINE_VERSION)


def test_corpus_provenance_and_chunk_limits():
    docs = load_documents()
    assert len(docs) >= 7
    assert len({d.metadata['chunk_id'] for d in docs}) == len(docs)
    for d in docs:
        assert len(d.page_content) <= 700
        assert d.metadata['url'].startswith(('https://help.openai.com/', 'https://openai.com/', 'https://learn.microsoft.com/', 'https://support.claude.com/', 'https://knowledge.workspace.google.com/'))
        assert d.metadata['reviewed']


def test_guard_cases():
    cases = json.loads((ROOT / 'evals/cases.json').read_text())
    for c in cases:
        if c['route'] != 'answer':
            scenario = Scenario(vendor=c.get('vendor', 'ChatGPT'), platform=c.get('platform', 'Microsoft 365'), plan=c.get('plan', 'Business'), method=c.get('method', 'Live SharePoint access'))
            assert input_guard(c['question'], scenario.model_dump()).route == c['route']


def test_sensitive_input_rejected():
    assert input_guard('Use sk-' + 'x' * 30, Scenario().model_dump()).route == 'abstain'
    assert input_guard('Assess alice@example.com', Scenario().model_dump()).route == 'abstain'


def test_citation_validation_rejects_unknown_and_empty():
    docs = load_documents()[:1]
    for citations in [[], ['invented']]:
        assert citation_errors({'sufficient_evidence': True, 'facts': [{'text': 'Fact', 'citations': citations}]}, docs)


class FakeStore:
    def __init__(self):
        self.filter_seen = False
    def similarity_search(self, query, k, **kwargs):
        self.filter_seen = 'filter' in kwargs
        docs = load_documents()
        if 'filter' in kwargs:
            docs = [d for d in docs if kwargs['filter'](d)]
        return docs[:k]


class FakeLLM:
    def __init__(self, grounded=True, citation='OAI-LIVE-1'):
        self.grounded = grounded
        self.citation = citation
    def with_structured_output(self, schema):
        outer = self
        class Runner:
            def invoke(self, messages):
                if schema == Gate:
                    return Gate(route='answer', message='')
                if schema == Grounding:
                    return Grounding(supported=outer.grounded, reason='Fixture check; not live evaluation')
                return Assessment(sufficient_evidence=True,
                                  facts=[{'text':'Work or school accounts are required.', 'citations':[outer.citation]}],
                                  recommendations=['Verify source permissions.'], unknowns=['Tenant not inspected.'])
        return Runner()


def test_graph_returns_supported_answer_with_filter():
    store = FakeStore()
    result = run(build_graph(store, FakeLLM()), 'What account is supported?', Scenario())
    assert result['route'] == 'answer'
    assert store.filter_seen
    assert result['assessment']


def test_graph_baseline_does_not_filter():
    store = FakeStore()
    run(build_graph(store, FakeLLM()), 'What account is supported?', Scenario(), 'baseline')
    assert not store.filter_seen


def test_failed_grounding_withholds_draft():
    result = run(build_graph(FakeStore(), FakeLLM(grounded=False)), 'What account is supported?', Scenario())
    assert result['route'] == 'abstain'
    assert result['assessment'] is None


def test_invented_citation_withholds_draft():
    result = run(build_graph(FakeStore(), FakeLLM(citation='fake')), 'What account is supported?', Scenario())
    assert result['route'] == 'abstain'
    assert result['assessment'] is None


def test_no_evidence_abstains():
    class Empty:
        def similarity_search(self, *args, **kwargs):
            return []
    result = run(build_graph(Empty(), FakeLLM()), 'What account is supported?', Scenario())
    assert result['route'] == 'abstain'
    assert 'generate: structured assessment' not in result['trace']


def test_wrong_vendor_citation_withheld_even_when_checker_would_pass():
    class MixedStore:
        def similarity_search(self, *args, **kwargs):
            return [d for d in load_documents() if d.metadata['vendor'] == 'Claude']
    result = run(build_graph(MixedStore(), FakeLLM(citation='CLAUDE-M365-1')),
                 'Does consent assign an admin role?', Scenario(), 'baseline')
    assert result['route'] == 'abstain'
    assert result['assessment'] is None
    assert 'another vendor' in result['message']


def test_filtered_search_rejects_store_results_that_ignore_filter():
    class BrokenFilterStore:
        def similarity_search(self, *args, **kwargs):
            return [d for d in load_documents() if d.metadata['vendor'] == 'Claude']
    result = run(build_graph(BrokenFilterStore(), FakeLLM()), 'What access is needed?', Scenario())
    assert result['route'] == 'abstain'
    assert result['evidence'] == []
    assert not any(t.startswith('generate:') for t in result['trace'])


def test_shared_platform_source_cannot_support_ai_plan_claim():
    docs = load_documents()
    assessment = {'plan_guidance': [{'text': 'ChatGPT Business may lack monitoring.', 'citations': ['MS-REVIEW-1']}]}
    assert scope_errors(assessment, docs, Scenario().model_dump())


def test_matching_vendor_and_shared_permission_sources_allowed():
    assessment = {'facts': [{'text': 'Consent is not role assignment.', 'citations': ['MS-PERM-2']}],
                  'plan_guidance': [{'text': 'Verify documented plan controls.', 'citations': ['OAI-ADMIN-1']}]}
    assert not scope_errors(assessment, load_documents(), Scenario().model_dump())


def test_missing_metadata_fails_closed():
    from langchain_core.documents import Document
    assert not evidence_matches(Document(page_content='Unlabelled source'), Scenario().model_dump())


def test_exports_identify_pipeline_and_corpus():
    result = run(build_graph(FakeStore(), FakeLLM()), 'What account is supported?', Scenario())
    assert result['pipeline_version'] == PIPELINE_VERSION
    assert len(result['corpus_sha256']) == 64
    assert result['completed_at_utc']
