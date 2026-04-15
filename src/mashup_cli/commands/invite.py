from __future__ import annotations

import typer

from ..client import APIError, MashupClient
from ..output import error, is_json_mode, print_json, print_table

app = typer.Typer(help="초대코드 관리")


@app.command("list")
def list_invite_codes(
    generation: int = typer.Argument(..., help="기수"),
):
    """초대코드 목록을 조회합니다."""
    client = MashupClient()
    try:
        data = client.get("/api/v1/invite-code", params={"generationNumber": generation})
    except APIError as e:
        error(str(e))

    codes = data if isinstance(data, list) else data.get("data", data)

    if is_json_mode():
        print_json(codes)
        return

    rows = [
        [c.get("inviteCodeId"), c.get("inviteCode"), c.get("platform"), c.get("validEndedAt")]
        for c in codes
    ]
    print_table(["ID", "코드", "플랫폼", "만료일"], rows)


@app.command("create")
def create_invite_code(
    generation: int = typer.Argument(..., help="기수"),
    platform: str = typer.Option(..., help="플랫폼"),
    expires_at: str = typer.Option(..., help="만료일 (ISO 8601)"),
):
    """초대코드를 생성합니다."""
    client = MashupClient()
    try:
        data = client.post(
            "/api/v1/invite-code",
            json={"generationNumber": generation, "platform": platform, "expiresAt": expires_at},
        )
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    code = data.get("data", data) if isinstance(data, dict) else data
    typer.echo(f"초대코드 생성 완료: {code}")
