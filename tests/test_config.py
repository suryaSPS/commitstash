import json

import pytest

from commitstash import config as config_mod


@pytest.fixture(autouse=True)
def _isolate_legacy(tmp_path, monkeypatch):
    """Keep a developer's real ~/.autocommit out of these tests."""
    monkeypatch.setattr(config_mod, "LEGACY_CONFIG_PATH", tmp_path / "absent-legacy.json")


def test_defaults_present():
    d = config_mod.DEFAULTS
    assert d["provider"] == "anthropic"
    assert d["scan_secrets"] is True
    assert d["ollama_model"]
    assert d["ollama_host"].startswith("http")


def test_load_returns_defaults_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "CONFIG_PATH", tmp_path / "config.json")
    cfg = config_mod.load_config()
    assert cfg["provider"] == "anthropic"
    assert cfg["scan_secrets"] is True


def test_load_merges_file_over_defaults(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"provider": "ollama", "style": "simple"}))
    monkeypatch.setattr(config_mod, "CONFIG_PATH", path)
    cfg = config_mod.load_config()
    assert cfg["provider"] == "ollama"
    assert cfg["style"] == "simple"
    # untouched keys still come from defaults
    assert cfg["scan_secrets"] is True


def test_save_strips_api_keys(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    monkeypatch.setattr(config_mod, "CONFIG_PATH", path)
    config_mod.save_config({"provider": "openai", "openai_api_key": "sk-secret"})
    saved = json.loads(path.read_text())
    assert "openai_api_key" not in saved
    assert saved["provider"] == "openai"


# ── legacy (pre-rename) config migration ──────────────────────────────────────


def _setup_paths(tmp_path, monkeypatch, legacy_text=None):
    new = tmp_path / "new" / "config.json"
    legacy = tmp_path / "old" / "config.json"
    if legacy_text is not None:
        legacy.parent.mkdir(parents=True)
        legacy.write_text(legacy_text)
    monkeypatch.setattr(config_mod, "CONFIG_PATH", new)
    monkeypatch.setattr(config_mod, "LEGACY_CONFIG_PATH", legacy)
    return new, legacy


def test_migrates_legacy_config(tmp_path, monkeypatch):
    new, legacy = _setup_paths(tmp_path, monkeypatch, json.dumps({"provider": "ollama"}))
    assert config_mod.migrate_legacy_config() is True
    assert json.loads(new.read_text()) == {"provider": "ollama"}
    # non-destructive: an older install still finds its config
    assert legacy.exists()


def test_load_config_picks_up_legacy_settings(tmp_path, monkeypatch):
    _setup_paths(tmp_path, monkeypatch, json.dumps({"provider": "ollama", "emoji": True}))
    cfg = config_mod.load_config()
    assert cfg["provider"] == "ollama"
    assert cfg["emoji"] is True


def test_migration_does_not_overwrite_existing_config(tmp_path, monkeypatch):
    new, _ = _setup_paths(tmp_path, monkeypatch, json.dumps({"provider": "ollama"}))
    new.parent.mkdir(parents=True)
    new.write_text(json.dumps({"provider": "openai"}))
    assert config_mod.migrate_legacy_config() is False
    assert json.loads(new.read_text()) == {"provider": "openai"}


def test_migration_noop_without_legacy_file(tmp_path, monkeypatch):
    new, _ = _setup_paths(tmp_path, monkeypatch)
    assert config_mod.migrate_legacy_config() is False
    assert not new.exists()


def test_corrupt_legacy_config_is_not_carried_forward(tmp_path, monkeypatch):
    new, _ = _setup_paths(tmp_path, monkeypatch, "{not valid json")
    assert config_mod.migrate_legacy_config() is False
    assert not new.exists()
    # and the CLI still starts on defaults rather than crashing
    assert config_mod.load_config()["provider"] == "anthropic"
