from __future__ import annotations

import sys

import httpx
import typer

from . import config, output


def login(api_url: str) -> None:
    username = typer.prompt("Username")
    password = typer.prompt("Password", hide_input=True)

    try:
        resp = httpx.post(
            f"{api_url}/api/v1/admin-members/login",
            json={"username": username, "password": password},
        )
    except httpx.ConnectError:
        output.error(f"서버에 연결할 수 없습니다: {api_url}")

    if resp.status_code == 401:
        print("아이디 또는 비밀번호가 올바르지 않습니다.", file=sys.stderr)
        raise SystemExit(1)
    if resp.status_code >= 400:
        output.error(f"로그인 실패: {resp.status_code}")

    data = resp.json()
    token = data.get("token") or data.get("accessToken") or data.get("data", {}).get("token")
    if not token:
        output.error(f"토큰을 찾을 수 없습니다. 응답: {data}")

    config.save({"api_url": api_url, "token": token})
    typer.echo("로그인 성공. 설정이 저장되었습니다.")
