from __future__ import annotations

from typing import Optional

import typer

from ..client import APIError, MashupClient
from ..output import error, is_json_mode, print_json, print_table

app = typer.Typer(help="멤버 관리")


@app.command("list")
def list_members(
    generation: int = typer.Argument(..., help="기수"),
    platform: Optional[str] = typer.Option(None, help="플랫폼 필터 (예: SPRING, iOS, WEB, ANDROID, NODE)"),
):
    """기수별 멤버 목록을 조회합니다."""
    client = MashupClient()
    params = {"generationNumber": generation}
    if platform:
        params["platform"] = platform
    try:
        data = client.get(f"/api/v1/members/{generation}", params=params)
    except APIError as e:
        error(str(e))

    members = data if isinstance(data, list) else data.get("data", data)

    if is_json_mode():
        print_json(members)
        return

    rows = [
        [m.get("memberId"), m.get("name"), m.get("platform"), m.get("memberStatus")]
        for m in members
    ]
    print_table(["ID", "이름", "플랫폼", "상태"], rows, footer=f"Total: {len(rows)} members")


@app.command("get")
def get_member(
    generation: int = typer.Argument(..., help="기수"),
    member_id: int = typer.Argument(..., help="멤버 ID"),
):
    """멤버 상세 정보를 조회합니다."""
    client = MashupClient()
    try:
        data = client.get(f"/api/v1/members/{generation}/{member_id}")
    except APIError as e:
        error(str(e))

    member = data.get("data", data)

    if is_json_mode():
        print_json(member)
        return

    from ..output import print_dict
    print_dict(member)


@app.command("reset-password")
def reset_password(
    member_id: int = typer.Argument(..., help="멤버 ID"),
):
    """멤버 비밀번호를 초기화합니다."""
    client = MashupClient()
    try:
        data = client.patch(f"/api/v1/members/{member_id}/reset/password")
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo("비밀번호가 초기화되었습니다.")


@app.command("status", hidden=True)
def update_status(
    generation: int = typer.Argument(..., help="기수"),
    status: str = typer.Option(..., help="변경할 상태 (ACTIVE, INACTIVE, DROP_OUT)"),
    member_ids: str = typer.Option(..., "--members", help="멤버 ID 목록 (콤마 구분)"),
):
    """멤버 상태를 변경합니다."""
    client = MashupClient()
    ids = [int(i.strip()) for i in member_ids.split(",")]
    try:
        data = client.post(
            f"/api/v1/members/status/{generation}",
            json={"memberIds": ids, "status": status},
        )
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo(f"상태가 {status}로 변경되었습니다.")


@app.command("transfer", hidden=True)
def transfer(
    from_gen: int = typer.Option(..., "--from", help="원본 기수"),
    to_gen: int = typer.Option(..., "--to", help="대상 기수"),
    member_ids: str = typer.Option(..., "--members", help="멤버 ID 목록 (콤마 구분)"),
):
    """멤버를 다른 기수로 이동합니다."""
    client = MashupClient()
    ids = [int(i.strip()) for i in member_ids.split(",")]
    try:
        data = client.post(
            "/api/v1/members/transfer",
            json={"memberIds": ids, "fromGenerationNumber": from_gen, "toGenerationNumber": to_gen},
        )
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo(f"{from_gen}기 → {to_gen}기 이동 완료.")
