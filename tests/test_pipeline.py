import json

from advisor.pipeline import (Assessment, Gate, Grounding, ROOT, Scenario,
                              build_graph, citation_errors, input_guard, load_documents, run)


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
