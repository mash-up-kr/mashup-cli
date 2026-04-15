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
    """스칼라 필드만 표시하고, 중첩 구조는 이름만 요약해 `--json` 사용을 안내한다.

    기존에는 리스트/딕셔너리를 str()로 바로 찍어 한 줄에 Python repr이 박혀
    읽기 어려웠음. 자세한 내용이 필요한 사용자는 `--json`으로 받아가게 한다.
    """
    nested_keys: list[str] = []
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            size = len(value)
            kind = "objects" if isinstance(value, list) else "fields"
            console.print(f"[bold]{key}[/bold]: [dim]<{size} {kind}, --json으로 전체 확인>[/dim]")
            nested_keys.append(key)
        else:
            display = "-" if value is None else value
            console.print(f"[bold]{key}[/bold]: {display}")

    if nested_keys:
        joined = ", ".join(nested_keys)
        console.print(
            f"\n[dim]중첩 필드({joined})는 `--json` 옵션으로 전체 구조를 확인하세요.[/dim]"
        )


def error(msg: str, exit_code: int = 2) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    raise SystemExit(exit_code)
