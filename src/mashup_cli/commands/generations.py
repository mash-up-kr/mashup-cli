from __future__ import annotations

import typer

from ..client import APIError, MashupClient
from ..output import error, is_json_mode, print_dict, print_json, print_table

app = typer.Typer(help="기수 관리")


@app.command("list")
def list_generations():
    """기수 목록을 조회합니다."""
    client = MashupClient()
    try:
        data = client.get("/api/v1/generations")
    except APIError as e:
        error(str(e))

    generations = data if isinstance(data, list) else data.get("data", data)

    if is_json_mode():
        print_json(generations)
        return

    rows = [[g.get("id"), g.get("number"), g.get("startedAt"), g.get("endedAt")] for g in generations]
    print_table(["ID", "기수", "시작일", "종료일"], rows)


@app.command("current")
def current_generation():
    """현재 활성화된 기수를 조회합니다."""
    client = MashupClient()
    try:
        data = client.get("/api/v1/generations")
    except APIError as e:
        error(str(e))

    gens = data if isinstance(data, list) else data.get("data", data)

    from datetime import date
    today = date.today().isoformat()
    current = next(
        (g for g in gens if g.get("startedAt", "") <= today <= g.get("endedAt", "")),
        None,
    )

    if current is None:
        print("현재 활성화된 기수가 없습니다.", file=__import__("sys").stderr)
        raise SystemExit(2)

    if is_json_mode():
        print_json(current)
        return

    print_dict(current)


@app.command("create", hidden=True)
def create_generation(
    number: int = typer.Option(..., help="기수 번호"),
    started_at: str = typer.Option(..., help="시작일 (YYYY-MM-DD)"),
    ended_at: str = typer.Option(..., help="종료일 (YYYY-MM-DD)"),
):
    """새 기수를 생성합니다."""
    client = MashupClient()
    try:
        data = client.post(
            "/api/v1/generations",
            json={"number": number, "startedAt": started_at, "endedAt": ended_at},
        )
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo(f"{number}기가 생성되었습니다.")
