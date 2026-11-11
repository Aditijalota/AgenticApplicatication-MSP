from streamlit.testing.v1 import AppTest
from advisor.pipeline import ROOT


def test_setup_screen_is_closed_without_secrets(monkeypatch):
    monkeypatch.delenv('APP_PASSWORD', raising=False)
    monkeypatch.delenv('LOCAL_DEMO', raising=False)
    app = AppTest.from_file(ROOT / 'app.py').run()
    assert not app.exception
    assert any('Setup required' in i.value for i in app.info)


def test_local_ui_and_clarification_without_model(monkeypatch):
    monkeypatch.setenv('LOCAL_DEMO', 'true')
    monkeypatch.delenv('APP_PASSWORD', raising=False)
    app = AppTest.from_file(ROOT / 'app.py').run()
    assert not app.exception
    assert len(app.tabs) == 3
    app.text_area[0].set_value('What permissions are required?')
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state['result']['route'] == 'clarify'


def test_password_gate(monkeypatch):
    monkeypatch.setenv('APP_PASSWORD', 'fixture-password-not-a-real-secret')
    app = AppTest.from_file(ROOT / 'app.py').run()
    assert not app.exception
    assert len(app.text_area) == 0
    app.text_input[0].set_value('wrong')
    app.button[0].click().run()
    assert any('Incorrect password' in x.value for x in app.error)
    app.text_input[0].set_value('fixture-password-not-a-real-secret')
    app.button[0].click().run()
    assert not app.exception
    assert len(app.text_area) == 1
