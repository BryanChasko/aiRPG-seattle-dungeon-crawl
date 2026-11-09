"""Floor Infinity tests: the reset tool. Temp dirs only; nothing real is deleted."""

import os

import pytest

import reset_multiverse
from reset_multiverse import check_paths, inventory, main


@pytest.fixture()
def rooms(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    home = tmp_path / "home"
    (root / "dungeon" / "5_a2a_integration" / "utils").mkdir(parents=True)
    kb = root / "dungeon" / "5_a2a_integration" / "utils" / "rules_knowledge_base"
    kb.mkdir()
    (kb / "index.json").write_text("{}")
    deep = root / "dungeon" / "encounters" / "save-points"
    deep.mkdir(parents=True)
    (deep / ".mid-song-save").mkdir()
    cache = home / ".cache" / "uv"
    cache.mkdir(parents=True)
    (cache / "blob").write_text("x")
    monkeypatch.setattr(reset_multiverse, "stop_servers", lambda ports: [])
    return root, home


def test_inventory_finds_seeded_rows(rooms):
    root, home = (str(p) for p in rooms)
    rows = {(r[1], r[3]) for r in inventory(root, home)}
    assert any(str(p).endswith("rules_knowledge_base") and s == "present" for p, s in rows)
    assert any(".mid-song-save" in str(p) and s == "present" for p, s in rows)


def test_inventory_reports_missing_as_gone(rooms):
    root, home = (str(p) for p in rooms)
    rows = {(r[1], r[3]) for r in inventory(root, home)}
    assert any(str(p).endswith(".venv") and s == "gone" for p, s in rows)


def test_dry_run_deletes_nothing(rooms, capsys):
    root, home = (str(p) for p in rooms)
    assert main([], root=root, home=home) == 0
    kb = os.path.join(root, "dungeon", "5_a2a_integration", "utils", "rules_knowledge_base")
    assert os.path.isdir(kb)


def test_apply_deletes_tier_1(rooms):
    root, home = (str(p) for p in rooms)
    assert main(["--apply", "--yes"], root=root, home=home) == 0
    kb = os.path.join(root, "dungeon", "5_a2a_integration", "utils", "rules_knowledge_base")
    assert not os.path.exists(kb)


def test_apply_keeps_caches_without_flag(rooms):
    root, home = (str(p) for p in rooms)
    assert main(["--apply", "--yes"], root=root, home=home) == 0
    assert os.path.isfile(os.path.join(home, ".cache", "uv", "blob"))


def test_caches_flag_clears_cache(rooms):
    root, home = (str(p) for p in rooms)
    assert main(["--apply", "--caches", "--yes"], root=root, home=home) == 0
    assert not os.path.exists(os.path.join(home, ".cache", "uv"))


def test_apply_is_idempotent(rooms):
    root, home = (str(p) for p in rooms)
    assert main(["--apply", "--yes"], root=root, home=home) == 0
    assert main(["--apply", "--yes"], root=root, home=home) == 0


def test_confirmation_no_skips_tier(rooms, monkeypatch):
    root, home = (str(p) for p in rooms)
    monkeypatch.setattr("builtins.input", lambda _prompt: "no")
    assert main(["--apply"], root=root, home=home) == 0
    kb = os.path.join(root, "dungeon", "5_a2a_integration", "utils", "rules_knowledge_base")
    assert os.path.isdir(kb)


def test_refuses_paths_outside_root_and_home(rooms):
    root, home = (str(p) for p in rooms)
    with pytest.raises(ValueError):
        check_paths([(1, "/etc/cron.d/crawl", "file", "present", 0)], root, home)


def test_verify_pass_lists_gone_after_apply(rooms, capsys):
    root, home = (str(p) for p in rooms)
    main(["--apply", "--yes"], root=root, home=home)
    out = capsys.readouterr().out
    assert "=== Verify ===" in out
