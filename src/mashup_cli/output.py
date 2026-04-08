from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()
_json_mode = False


def set_json_mode(enabled: bool) -> None:
    global _json_mode
    _json_mode = enabled


def is_json_mode() -> bool:
    return _json_mode


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def print_table(columns: list[str], rows: list[list[Any]], footer: str | None = None) -> None:
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", style="dim", width=4)
    for col in columns:
        table.add_column(col)
    for i, row in enumerate(rows, 1):
        table.add_row(str(i), *[str(v) if v is not None else "-" for v in row])
    console.print(table)
    if footer:
        console.print(f"\n[dim]{footer}[/dim]")


def print_dict(data: dict) -> None:
    for key, value in data.items():
        console.print(f"[bold]{key}[/bold]: {value}")


def error(msg: str, exit_code: int = 2) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    raise SystemExit(exit_code)
