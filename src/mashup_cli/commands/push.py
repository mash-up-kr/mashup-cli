from __future__ import annotations

from typing import Optional

import typer

from ..client import APIError, MashupClient
from ..output import error, is_json_mode, print_json

app = typer.Typer(help="푸시 알림")


@app.command("broadcast")
def broadcast(
    title: str = typer.Option(..., help="알림 제목"),
    body: str = typer.Option(..., help="알림 내용"),
):
    """전체 멤버에게 푸시 알림을 보냅니다."""
    client = MashupClient()
    try:
        data = client.post("/api/v1/push-notis/broadcast", json={"title": title, "body": body})
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo("전체 푸시 알림이 발송되었습니다.")


@app.command("narrowcast")
def narrowcast(
    title: str = typer.Option(..., help="알림 제목"),
    body: str = typer.Option(..., help="알림 내용"),
    members: str = typer.Option(..., "--members", help="멤버 ID 목록 (콤마 구분)"),
):
    """선택된 멤버에게 푸시 알림을 보냅니다."""
    client = MashupClient()
    member_ids = [int(i.strip()) for i in members.split(",")]
    try:
        data = client.post(
            "/api/v1/push-notis/narrowcast",
            json={"title": title, "body": body, "memberIds": member_ids},
        )
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo(f"{len(member_ids)}명에게 푸시 알림이 발송되었습니다.")
