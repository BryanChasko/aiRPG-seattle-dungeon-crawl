"""Floor 9.2 tests: the FogGate and store_memory. No model, no memory service."""

from types import SimpleNamespace

import memory_gate
from memory_gate import FOG_MARKERS, STORED, FogGate, store_memory


def _event(text):
    return SimpleNamespace(message={"role": "assistant", "content": [{"text": text}]})


def setup_function(_):
    STORED.clear()


def test_clean_message_commits():
    gate = FogGate()
    gate._check(_event("Ties go to the higher Groove."))
    assert gate.committed == ["Ties go to the higher Groove."]
    assert gate.quarantined == []


def test_louder_dancer_quarantines_with_reason():
    gate = FogGate()
    gate._check(_event("Ties go to the louder dancer."))
    assert gate.committed == []
    assert len(gate.quarantined) == 1
    assert "louder dancer" in gate.quarantined[0][1]


def test_steam_marker_quarantines():
    gate = FogGate()
    gate._check(_event("The fog is mostly steam, trust it."))
    assert gate.committed == []


def test_drum_marker_quarantines():
    gate = FogGate()
    gate._check(_event("The drum decides ties by volume."))
    assert gate.committed == []


def test_markers_match_case_insensitively():
    gate = FogGate()
    gate._check(_event("Ties go to the LOUDER DANCER."))
    assert gate.committed == []
    assert len(gate.quarantined) == 1


def test_plain_string_message_commits():
    gate = FogGate()
    gate._check(SimpleNamespace(message="Cordula banks 2 Groove."))
    assert gate.committed == ["Cordula banks 2 Groove."]


def test_register_hooks_watches_message_added():
    from strands.hooks.events import MessageAddedEvent

    seen = {}
    registry = SimpleNamespace(add_callback=lambda *a, **k: seen.update({"args": a}))
    gate = FogGate()
    gate.register_hooks(registry)
    assert seen["args"][0] is MessageAddedEvent
    gate2 = FogGate()
    seen["args"][1](_event("Ties go to the higher Groove."))
    assert gate.committed == ["Ties go to the higher Groove."]
    assert gate2.committed == []


def test_every_marker_fires():
    gate = FogGate()
    for marker in FOG_MARKERS:
        gate._check(_event("Fog says " + marker + "."))
    assert gate.committed == []
    assert len(gate.quarantined) == len(FOG_MARKERS)


def test_store_memory_records_and_returns_stored():
    assert store_memory("Cordula banks 2 Groove.") == "stored"
    assert STORED == ["Cordula banks 2 Groove."]
