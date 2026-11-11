import pytest
from advisor.pipeline import Scenario, input_guard, load_documents, evidence_matches, citation_errors
from advisor.ticket import render_ticket


def test_vendor_filter_does_not_mix_evidence():
    for vendor, platform in [('ChatGPT','Microsoft 365'),('Claude','Microsoft 365'),('Gemini','Google Workspace')]:
        docs = [d for d in load_documents() if evidence_matches(d, {'vendor':vendor,'platform':platform})]
        assert docs
        assert all(d.metadata['vendor'] in ('shared', vendor) for d in docs)
        assert all(d.metadata['platform'] == platform for d in docs)


def test_cross_platform_request_is_withheld():
    s = Scenario(vendor='Gemini', platform='Microsoft 365')
    assert input_guard('Read my files',s.model_dump()).route == 'abstain'


def test_permission_input_cannot_carry_secrets():
    s = Scenario(requested_permissions='sk-'+'x'*30)
    assert input_guard('Review requested permissions',s.model_dump()).route == 'abstain'


def test_control_citations_are_checked():
    assert citation_errors({'controls':[{'citations':['made-up']} ]}, load_documents())


def test_ticket_requires_review_and_supported_result():
    result={'route':'answer','assessment':{'facts':[],'unknowns':['Exact scopes unknown.']}}
    with pytest.raises(ValueError):
        render_ticket(result,False)
    with pytest.raises(ValueError):
        render_ticket({'route':'abstain'},True)
    text=render_ticket(result,True)
    assert 'AUTHORIZATION PENDING' in text
    assert 'Exact scopes unknown.' in text
    assert 'Controls are incomplete' in text
