from __future__ import annotations

import typer

from ..client import APIError, MashupClient
from ..output import error, is_json_mode, print_json, print_table

app = typer.Typer(help="KV 저장소")


@app.command("get")
def get_value(
    key: str = typer.Argument(..., help="키"),
):
    """KV 저장소에서 값을 조회합니다."""
    client = MashupClient()
    try:
        data = client.get(f"/api/v1/storage/key/{key}")
    except APIError as e:
        error(str(e))

    # 응답 스키마: {"code": "SUCCESS", "data": {"keyString": "...", "valueMap": {...}}}
    payload = data.get("data", data) if isinstance(data, dict) else data
    value = payload.get("valueMap", payload) if isinstance(payload, dict) else payload

    if is_json_mode():
        print_json(value)
        return

    typer.echo(f"{key} = {value}")


@app.command("set")
def set_value(
    key: str = typer.Argument(..., help="키"),
    value: str = typer.Argument(..., help="값"),
):
    """KV 저장소에 값을 설정합니다."""
    client = MashupClient()
    try:
        data = client.post("/api/v1/storage", json={"key": key, "value": value})
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo(f"{key} = {value} 저장 완료.")


@app.command("keys")
def list_keys():
    """KV 저장소의 모든 키를 조회합니다."""
    client = MashupClient()
    try:
        data = client.get("/api/v1/storage/keys")
    except APIError as e:
        error(str(e))

    # 실제 응답 스키마: {"code": "SUCCESS", "data": {"keyStrings": [...]}}.
    # envelope를 한 단계 벗긴 뒤 keyStrings를 꺼낸다.
    # 과거 포맷(list 자체 / {"data": [...]})도 방어적으로 처리.
    payload = data.get("data", data) if isinstance(data, dict) else data
    if isinstance(payload, list):
        keys = payload
    elif isinstance(payload, dict):
        keys = payload.get("keyStrings") or []
    else:
        keys = []

    if is_json_mode():
        print_json(keys)
        return

    rows = (
        [[k] for k in keys]
        if keys and isinstance(keys[0], str)
        else [[k.get("key")] for k in keys]
    )
    print_table(["키"], rows, footer=f"Total: {len(rows)} keys")
