from __future__ import annotations

from typing import Optional

import typer

from . import auth, config, output
from .client import APIError
from .commands import applications, generations, invite, members, push, schedules, score, storage

app = typer.Typer(
    name="mashup",
    help="Mash-Up Admin CLI — 운영진용 터미널 도구",
    no_args_is_help=True,
)

# 서브커맨드 등록
app.add_typer(members.app, name="members")
app.add_typer(generations.app, name="generations")
app.add_typer(schedules.app, name="schedules")
app.add_typer(applications.app, name="applications")
app.add_typer(push.app, name="push")
app.add_typer(invite.app, name="invite")
app.add_typer(score.app, name="score")
app.add_typer(storage.app, name="storage")


@app.callback()
def global_options(
    json: bool = typer.Option(False, "--json", help="JSON 출력 (AI Agent용)"),
    verbose: bool = typer.Option(False, "--verbose", help="상세 로그"),
):
    output.set_json_mode(json)


@app.command()
def login(
    url: str = typer.Option("https://api.adminsoo.mash-up.kr", "--url", help="API 서버 URL"),
):
    """Admin 로그인 후 JWT를 저장합니다."""
    auth.login(url)


@app.command()
def whoami():
    """현재 로그인된 관리자 정보를 조회합니다."""
    from .client import MashupClient

    client = MashupClient()
    try:
        data = client.get("/api/v1/admin-members/me")
    except APIError as e:
        output.error(str(e))

    me = data.get("data", data)

    if output.is_json_mode():
        output.print_json(me)
        return

    output.print_dict(me)


@app.command()
def logout():
    """저장된 토큰을 삭제합니다."""
    config.clear()
    typer.echo("로그아웃 완료.")


if __name__ == "__main__":
    app()
