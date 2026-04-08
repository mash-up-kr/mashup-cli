from __future__ import annotations

import typer

from ..client import APIError, MashupClient
from ..output import error, is_json_mode, print_dict, print_json, print_table

app = typer.Typer(help="지원서 관리")


@app.command("list", hidden=True)
def list_applications(
    generation: int = typer.Argument(..., help="기수"),
):
    """기수별 지원서 목록을 조회합니다."""
    client = MashupClient()
    try:
        data = client.get("/api/v1/applications", params={"generationNumber": generation})
    except APIError as e:
        error(str(e))

    applications = data if isinstance(data, list) else data.get("data", data)

    if is_json_mode():
        print_json(applications)
        return

    rows = [
        [a.get("id"), a.get("name"), a.get("platform"), a.get("result")]
        for a in applications
    ]
    print_table(["ID", "이름", "플랫폼", "결과"], rows)


@app.command("get", hidden=True)
def get_application(
    application_id: int = typer.Argument(..., help="지원서 ID"),
):
    """지원서 상세 정보를 조회합니다."""
    client = MashupClient()
    try:
        data = client.get(f"/api/v1/applications/{application_id}")
    except APIError as e:
        error(str(e))

    application = data.get("data", data)

    if is_json_mode():
        print_json(application)
        return

    print_dict(application)


@app.command("update-result", hidden=True)
def update_result(
    application_id: int = typer.Argument(..., help="지원서 ID"),
    result: str = typer.Option(..., help="결과 (PASS, FAIL)"),
):
    """지원서 합격/불합격 처리합니다."""
    client = MashupClient()
    try:
        data = client.post(
            f"/api/v1/applications/{application_id}/update-result",
            json={"result": result},
        )
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo(f"결과가 {result}로 변경되었습니다.")


@app.command("csv", hidden=True)
def download_csv(
    generation: int = typer.Argument(..., help="기수"),
    output_file: str = typer.Option("applications.csv", "--output", "-o", help="저장할 파일명"),
):
    """지원서를 CSV로 다운로드합니다."""
    import httpx
    from .. import config

    api_url = config.get("api_url", "")
    token = config.get("token", "")

    try:
        resp = httpx.get(
            f"{api_url}/api/v1/applications/csv",
            params={"generationNumber": generation},
            headers={"Authorization": f"Bearer {token}"},
        )
    except httpx.ConnectError:
        error(f"서버에 연결할 수 없습니다: {api_url}")

    if resp.status_code >= 400:
        error(f"CSV 다운로드 실패: {resp.status_code}")

    with open(output_file, "wb") as f:
        f.write(resp.content)

    typer.echo(f"저장 완료: {output_file}")
