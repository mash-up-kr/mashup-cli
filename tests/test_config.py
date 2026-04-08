from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".mashup"
        config_file = config_dir / "config.json"

        with patch("mashup_cli.config.CONFIG_DIR", config_dir), \
             patch("mashup_cli.config.CONFIG_FILE", config_file):
            from mashup_cli import config
            config.save({"api_url": "https://example.com", "token": "abc"})
            data = config.load()

        assert data["api_url"] == "https://example.com"
        assert data["token"] == "abc"


def test_load_missing_returns_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "nonexistent.json"
        with patch("mashup_cli.config.CONFIG_FILE", config_file):
            from mashup_cli import config
            assert config.load() == {}
