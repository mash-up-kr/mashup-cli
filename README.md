# mashup-cli

Mash-Up Admin API를 래핑하는 Python CLI.
운영진이 터미널에서 빠르게 조회/관리하고, AI Agent가 shell 명령으로 호출할 수 있다.

## 설치

```bash
pipx install mashup-cli
```

## 빠른 시작

```bash
# 로그인
mashup login --url https://api.adminsoo.mash-up.kr

# 멤버 목록 조회
mashup members list 14

# AI Agent용 JSON 출력
mashup --json members list 14
```

## 커맨드

| 커맨드 | 설명 |
|--------|------|
| `mashup login` | Admin 로그인 → JWT 저장 |
| `mashup whoami` | 현재 로그인된 관리자 정보 |
| `mashup logout` | 토큰 삭제 |
| `mashup members list <기수>` | 기수별 멤버 목록 |
| `mashup members get <기수> <멤버ID>` | 멤버 상세 |
| `mashup generations list` | 기수 목록 |
| `mashup schedules list <기수>` | 일정 목록 |
| `mashup schedules get <일정ID>` | 일정 상세 |

전체 커맨드는 `mashup --help` 참조.

## 설정

로그인 후 `~/.mashup/config.json`에 저장됨:

```json
{
  "api_url": "https://api.adminsoo.mash-up.kr",
  "token": "eyJhbGciOiJ..."
}
```

## AI Agent 친화 설계

- `--json` 플래그: 구조화된 JSON 출력
- `--help`: Agent가 사용법을 스스로 파악
- 종료 코드: `0` 성공 / `1` 인증 실패 / `2` API 에러 / `3` 입력 오류
- stderr: 에러 메시지 / stdout: 순수 데이터

## 개발

```bash
git clone https://github.com/mash-up-kr/mashup-cli
cd mashup-cli
pip install -e ".[dev]"
pytest
```
