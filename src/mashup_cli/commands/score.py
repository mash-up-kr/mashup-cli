from __future__ import annotations

import typer

from ..client import APIError, MashupClient
from ..output import error, is_json_mode, print_json

app = typer.Typer(help="점수 관리")


@app.command("add")
def add_score(
    member_id: int = typer.Argument(..., help="멤버 ID"),
    score: int = typer.Option(..., help="점수"),
    reason: str = typer.Option(..., help="사유"),
):
    """멤버에게 점수를 부여합니다."""
    client = MashupClient()
    try:
        data = client.post(
            "/api/v1/score-history/add",
            json={"memberId": member_id, "score": score, "reason": reason},
        )
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo(f"점수 {score}점이 부여되었습니다.")


@app.command("cancel")
def cancel_score(
    score_id: int = typer.Argument(..., help="점수 기록 ID"),
):
    """점수를 취소합니다."""
    client = MashupClient()
    try:
        data = client.post("/api/v1/score-history/cancel", json={"scoreHistoryId": score_id})
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo("점수가 취소되었습니다.")
