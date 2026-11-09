"""Floor 9.1 tests: the fog verifier. All offline; the model is faked."""

from types import SimpleNamespace

import verifier
from verifier import Verdict, create_verifier, verify_claim


class _FakeAgent:
    def __init__(self, verdict):
        self.calls = {}
        self._verdict = verdict

    def __call__(self, prompt):
        self.calls["prompt"] = prompt
        return SimpleNamespace(structured_output=self._verdict)


def _fake_agent(verdict):
    return _FakeAgent(verdict)


def test_verdict_requires_a_call_but_defaults_citations():
    v = Verdict(supported=False)
    assert v.supported is False
    assert v.citations == []


def test_verdict_carries_citations():
    v = Verdict(supported=True, citations=["Groove"])
    assert v.citations == ["Groove"]


def test_create_verifier_uses_verdict_model(monkeypatch):
    monkeypatch.setattr(verifier, "BedrockModel", lambda **kw: SimpleNamespace(**kw))
    seen = {}

    class FakeAgent:
        def __init__(self, **kw):
            seen.update(kw)

    monkeypatch.setattr(verifier, "Agent", FakeAgent)
    create_verifier()
    assert seen["structured_output_model"] is Verdict


def test_create_verifier_runs_nova_2_lite(monkeypatch):
    captured = {}
    monkeypatch.setattr(verifier, "BedrockModel", lambda **kw: captured.update(kw) or SimpleNamespace(**kw))
    monkeypatch.setattr(verifier, "Agent", lambda **kw: SimpleNamespace(**kw))
    create_verifier()
    assert "nova-2-lite" in captured["model_id"]


def test_create_verifier_budgets_tokens(monkeypatch):
    captured = {}
    monkeypatch.setattr(verifier, "BedrockModel", lambda **kw: captured.update(kw) or SimpleNamespace(**kw))
    monkeypatch.setattr(verifier, "Agent", lambda **kw: SimpleNamespace(**kw))
    create_verifier()
    assert captured["max_tokens"] == 1024


def test_verify_claim_returns_supported(monkeypatch):
    fake = _fake_agent(Verdict(supported=True, citations=["Groove"]))
    monkeypatch.setattr(verifier, "create_verifier", lambda: fake)
    out = verify_claim("Ties go to the higher Groove.", ["15 Groove: ties go to the higher Groove."])
    assert out.supported is True
    assert out.citations == ["Groove"]


def test_verify_claim_returns_unsupported_for_fog(monkeypatch):
    fake = _fake_agent(Verdict(supported=False, citations=[]))
    monkeypatch.setattr(verifier, "create_verifier", lambda: fake)
    out = verify_claim("Ties go to the louder dancer.", ["15 Groove: ties go to the higher Groove."])
    assert out.supported is False


def test_verify_claim_prompt_carries_claim_and_passages(monkeypatch):
    fake = _fake_agent(Verdict(supported=True, citations=["Groove"]))
    monkeypatch.setattr(verifier, "create_verifier", lambda: fake)
    verify_claim("Ties go to the higher Groove.", ["15 Groove: ties go to the higher Groove."])
    assert "higher Groove" in fake.calls["prompt"]
    assert "15 Groove" in fake.calls["prompt"]


def test_verifier_prompt_demands_handbook_evidence():
    assert "handbook" in verifier.VERIFIER_PROMPT.lower()
