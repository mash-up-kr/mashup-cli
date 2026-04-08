from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".mashup"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def save(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))


def get(key: str, default=None):
    return load().get(key, default)


def set_value(key: str, value: str) -> None:
    data = load()
    data[key] = value
    save(data)


def clear() -> None:
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
