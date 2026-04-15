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

    if resp.status_code >= 400:
        # API가 내려준 에러 메시지를 최대한 드러낸다.
        # 예) 404 ADMIN_MEMBER_NOT_FOUND, 400 ADMIN_MEMBER_LOGIN_FAILED
        try:
            body = resp.json()
            code = body.get("code", "")
            message = body.get("message") or body.get("error") or ""
            detail = f"[{code}] {message}".strip(" []")
        except Exception:
            detail = resp.text[:200]
        print(
            f"로그인 실패 (HTTP {resp.status_code}): {detail}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    data = resp.json()
    # 응답 스키마: {"code": "SUCCESS", "data": {"accessToken": "..."}}
    nested = data.get("data") or {}
    token = (
        nested.get("accessToken")
        or nested.get("token")
        or data.get("accessToken")
        or data.get("token")
    )
    if not token:
        # 실패 응답에 토큰이 통째로 실리는 일은 없어야 하므로 key 목록만 노출.
        output.error(f"토큰을 찾을 수 없습니다. 응답 키: {list(data.keys())}")

    config.save({"api_url": api_url, "token": token})
    typer.echo("로그인 성공. 설정이 저장되었습니다.")
