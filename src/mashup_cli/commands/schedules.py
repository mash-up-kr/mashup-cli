from __future__ import annotations

from typing import Optional

import typer

from ..client import APIError, MashupClient
from ..output import error, is_json_mode, print_dict, print_json, print_table

app = typer.Typer(help="일정 관리")


@app.command("list")
def list_schedules(
    generation: int = typer.Argument(..., help="기수"),
    schedule_type: Optional[str] = typer.Option(None, help="일정 유형 필터"),
):
    """기수별 일정 목록을 조회합니다."""
    client = MashupClient()
    params: dict = {"generationNumber": generation}
    if schedule_type:
        params["scheduleType"] = schedule_type
    try:
        data = client.get("/api/v1/schedules", params=params)
    except APIError as e:
        error(str(e))

    schedules = data if isinstance(data, list) else data.get("data", data)

    if is_json_mode():
        print_json(schedules)
        return

    rows = [
        [s.get("id"), s.get("name"), s.get("startedAt"), s.get("endedAt"), s.get("status")]
        for s in schedules
    ]
    print_table(["ID", "이름", "시작", "종료", "상태"], rows)


@app.command("get")
def get_schedule(
    schedule_id: int = typer.Argument(..., help="일정 ID"),
):
    """일정 상세 정보를 조회합니다."""
    client = MashupClient()
    try:
        data = client.get(f"/api/v1/schedules/{schedule_id}")
    except APIError as e:
        error(str(e))

    schedule = data.get("data", data)

    if is_json_mode():
        print_json(schedule)
        return

    print_dict(schedule)


@app.command("next")
def next_schedule(
    generation: Optional[int] = typer.Option(None, help="기수 (생략 시 현재 기수)"),
):
    """가장 가까운 다음 일정을 조회합니다."""
    client = MashupClient()

    if generation is None:
        try:
            gens = client.get("/api/v1/generations")
            gens = gens if isinstance(gens, list) else gens.get("data", gens)
            from datetime import date
            today = date.today().isoformat()
            current = next(
                (g for g in gens if g.get("startedAt", "") <= today <= g.get("endedAt", "")),
                None,
            )
            if current is None:
                error("현재 활성화된 기수를 찾을 수 없습니다. --generation 옵션으로 기수를 지정하세요.")
            generation = current["number"]
        except APIError as e:
            error(str(e))

    try:
        data = client.get("/api/v1/schedules", params={"generationNumber": generation})
    except APIError as e:
        error(str(e))

    schedules = data if isinstance(data, list) else data.get("data", data)

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    upcoming = [s for s in schedules if (s.get("startedAt") or "") > now]
    upcoming.sort(key=lambda s: s.get("startedAt", ""))

    if not upcoming:
        typer.echo("예정된 일정이 없습니다.")
        raise SystemExit(0)

    nxt = upcoming[0]

    if is_json_mode():
        print_json(nxt)
        return

    print_dict(nxt)


@app.command("publish")
def publish_schedule(
    schedule_id: int = typer.Argument(..., help="일정 ID"),
):
    """일정을 공개합니다."""
    client = MashupClient()
    try:
        client.post(f"/api/v1/schedules/{schedule_id}/publish")
    except APIError as e:
        error(str(e))
    typer.echo("일정이 공개되었습니다.")


@app.command("hide")
def hide_schedule(
    schedule_id: int = typer.Argument(..., help="일정 ID"),
):
    """일정을 숨깁니다."""
    client = MashupClient()
    try:
        client.post(f"/api/v1/schedules/{schedule_id}/hide")
    except APIError as e:
        error(str(e))
    typer.echo("일정이 숨겨졌습니다.")


@app.command("qr", hidden=True)
def set_qr(
    schedule_id: int = typer.Argument(..., help="일정 ID"),
    event_id: int = typer.Argument(..., help="이벤트 ID"),
    started_at: str = typer.Option(..., help="QR 시작 시각 (ISO 8601)"),
    ended_at: str = typer.Option(..., help="QR 종료 시각 (ISO 8601)"),
):
    """이벤트 QR 출석 시간을 설정합니다."""
    client = MashupClient()
    try:
        data = client.post(
            f"/api/v1/schedules/{schedule_id}/event/{event_id}/qr",
            json={"startedAt": started_at, "endedAt": ended_at},
        )
    except APIError as e:
        error(str(e))

    if is_json_mode():
        print_json(data)
        return

    typer.echo("QR 시간이 설정되었습니다.")
