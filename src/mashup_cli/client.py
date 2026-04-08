from __future__ import annotations

import sys
from typing import Any

import httpx

from . import config


class APIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(message)


class MashupClient:
    def __init__(self):
        self.api_url = config.get("api_url", "")
        self.token = config.get("token", "")

        if not self.api_url:
            print("설정이 없습니다. 먼저 'mashup login'을 실행하세요.", file=sys.stderr)
            raise SystemExit(1)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _handle_response(self, resp: httpx.Response) -> Any:
        if resp.status_code == 401:
            print("인증이 만료되었습니다. 'mashup login'으로 다시 로그인하세요.", file=sys.stderr)
            raise SystemExit(1)
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise APIError(resp.status_code, str(detail))
        return resp.json()

    def get(self, path: str, params: dict | None = None) -> Any:
        with httpx.Client() as client:
            resp = client.get(
                f"{self.api_url}{path}",
                params=params,
                headers=self._headers(),
            )
        return self._handle_response(resp)

    def post(self, path: str, json: dict | None = None) -> Any:
        with httpx.Client() as client:
            resp = client.post(
                f"{self.api_url}{path}",
                json=json,
                headers=self._headers(),
            )
        return self._handle_response(resp)

    def patch(self, path: str, json: dict | None = None) -> Any:
        with httpx.Client() as client:
            resp = client.patch(
                f"{self.api_url}{path}",
                json=json,
                headers=self._headers(),
            )
        return self._handle_response(resp)

    def put(self, path: str, json: dict | None = None) -> Any:
        with httpx.Client() as client:
            resp = client.put(
                f"{self.api_url}{path}",
                json=json,
                headers=self._headers(),
            )
        return self._handle_response(resp)
