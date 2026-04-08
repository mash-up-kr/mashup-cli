# PRD: Mashup CLI

- **CLI 레포지토리**: https://github.com/mash-up-kr/mashup-cli
- **서버 레포지토리**: https://github.com/mash-up-kr/mashup-server

## 1. 배경

Mash-Up 운영진은 멤버 관리, 출석 확인, 일정 관리 등을 웹 어드민에서 수행한다.
AI Agent (Claude Code, Gemini 등)가 이 데이터에 접근하거나 운영 작업을 자동화하려면,
터미널에서 호출할 수 있는 CLI 도구가 필요하다.

## 2. 목표

Mash-Up Admin API를 래핑하는 Python CLI를 만들어,
운영진이 터미널에서 빠르게 조회/관리하고, AI Agent가 shell 명령으로 호출할 수 있도록 한다.

## 3. 사용자

| 사용자 | 사용 방식 |
|--------|-----------|
| 운영진 | 터미널에서 직접 실행 (`mashup members list 14`) |
| AI Agent | shell 명령 호출 + JSON 출력 파싱 (`mashup --json members list 14`) |

## 4. 기술 스택

| 항목 | 선택 | 이유 |
|------|------|------|
| 언어 | Python 3.10+ | AI Agent 생태계 주류, 빠른 개발 |
| CLI 프레임워크 | typer | 타입 힌트 기반 자동 help, Agent가 `--help`로 사용법 파악 |
| HTTP 클라이언트 | httpx | async 지원, requests 대비 모던 |
| 출력 포맷 | rich (테이블) + JSON | 사람: rich 테이블, Agent: `--json` 플래그 |
| 패키징 | pip / pipx | `pipx install mashup-cli` |
| 설정 저장 | `~/.mashup/config.json` | API URL, JWT 토큰 저장 |

## 5. 인증

```bash
# 초기 설정
mashup login --url https://admin-api.mashup.kr
# → username/password 입력 → JWT 발급 → ~/.mashup/config.json 저장

# 이후 자동으로 저장된 토큰 사용
mashup members list 14
```

`~/.mashup/config.json`:
```json
{
  "api_url": "https://admin-api.mashup.kr",
  "token": "eyJhbGciOiJ..."
}
```

토큰 만료 시 자동으로 재로그인 안내.

## 6. 커맨드 구조

### 6.1 인증

```bash
mashup login                      # Admin 로그인 → JWT 저장
mashup whoami                     # 현재 로그인된 관리자 정보
mashup logout                     # 토큰 삭제
```

### 6.2 멤버 관리

```bash
mashup members list <기수>                     # 기수별 멤버 목록
mashup members get <기수> <멤버ID>             # 멤버 상세
mashup members reset-password <멤버ID>         # 비밀번호 초기화
# [비활성화] mashup members status <기수> --status ACTIVE   # 멤버 상태 변경
mashup members transfer --from 13 --to 14      # 기수 이동
```

### 6.3 기수/팀

```bash
mashup generations list              # 기수 목록
# [비활성화] mashup generations create            # 기수 생성
mashup teams list <기수>             # 팀 목록
mashup teams create <기수>           # 팀 생성
```

### 6.4 일정/출석

```bash
mashup schedules list <기수>                    # 일정 목록
mashup schedules get <일정ID>                   # 일정 상세
mashup schedules create                         # 일정 생성 (인터랙티브)
mashup schedules publish <일정ID>               # 일정 공개
mashup schedules hide <일정ID>                  # 일정 숨김
mashup schedules qr <일정ID> <이벤트ID>         # QR 출석 시간 설정

mashup attendance list <일정ID>                 # 일정별 출석 현황 (플랫폼별)
mashup attendance get <일정ID> <멤버ID>         # 멤버별 출석 상태
mashup attendance update <일정ID> <이벤트ID> <멤버ID> --status ATTENDANCE  # 출석 상태 변경
```

> **참고**: `attendance update` 명령은 현재 Admin API에 없으므로, 서버에 출석 상태 변경 API 추가가 선행되어야 한다.
> 필요한 서버 작업은 [12. 서버 API 추가 필요 사항](#12-서버-api-추가-필요-사항) 참조.

### 6.5 지원서/모집

```bash
# [비활성화] mashup applications list <기수>                 # 지원서 목록
# [비활성화] mashup applications get <지원서ID>              # 지원서 상세
# [비활성화] mashup applications update-result <지원서ID>    # 합격/불합격 처리
# [비활성화] mashup applications csv <기수>                  # CSV 다운로드

mashup forms list                               # 설문지 목록
mashup forms get <설문지ID>                     # 설문지 상세
mashup forms create                             # 설문지 생성
```

### 6.6 알림

```bash
mashup push broadcast --title "제목" --body "내용"              # 전체 푸시
mashup push narrowcast --members 1,2,3 --title "제목" --body "내용"  # 선택 푸시
mashup email send                                               # 이메일 발송
mashup email list                                               # 발송 이력
```

### 6.7 기타

```bash
mashup invite list <기수>            # 초대코드 목록
mashup invite create <기수>          # 초대코드 생성
mashup score add <멤버ID>            # 점수 부여
mashup score cancel <점수ID>         # 점수 취소
mashup storage get <key>             # KV 저장소 조회
mashup storage set <key> <value>     # KV 저장소 설정
mashup storage keys                  # 키 목록
```

### 6.8 글로벌 옵션

```bash
--json          # JSON 출력 (AI Agent용)
--verbose       # 상세 로그
--help          # 도움말 (AI Agent가 자동 참조)
```

## 7. 출력 예시

### 사람 (기본):
```
$ mashup members list 14

 # │ ID  │ 이름     │ 플랫폼  │ 상태
───┼─────┼──────────┼─────────┼──────
 1 │ 42  │ 홍길동   │ Spring  │ ACTIVE
 2 │ 43  │ 김철수   │ iOS     │ ACTIVE
 3 │ 44  │ 이영희   │ Web     │ DROP_OUT

Total: 3 members
```

### AI Agent (`--json`):
```json
[
  {"id": 42, "name": "홍길동", "platform": "Spring", "status": "ACTIVE"},
  {"id": 43, "name": "김철수", "platform": "iOS", "status": "ACTIVE"},
  {"id": 44, "name": "이영희", "platform": "Web", "status": "DROP_OUT"}
]
```

## 8. 프로젝트 구조

```
mashup-cli/
├── pyproject.toml            # 패키지 설정
├── src/
│   └── mashup_cli/
│       ├── __init__.py
│       ├── main.py           # typer app, 글로벌 옵션
│       ├── config.py         # ~/.mashup/config.json 관리
│       ├── client.py         # httpx 기반 API 클라이언트
│       ├── auth.py           # 로그인/토큰 관리
│       ├── output.py         # rich 테이블 / JSON 출력
│       └── commands/
│           ├── members.py
│           ├── generations.py
│           ├── schedules.py
│           ├── applications.py
│           ├── push.py
│           ├── invite.py
│           ├── score.py
│           └── storage.py
└── tests/
```

## 9. 구현 우선순위

### Phase 1 (MVP)
- `login` / `whoami` / `logout`
- `members list` / `members get`
- `generations list`
- `schedules list` / `schedules get`
- `--json` 글로벌 옵션

### Phase 2
- `attendance list` / `attendance get` / `attendance update` (서버 API 추가 선행 필요)
- `push broadcast` / `push narrowcast`
- `applications list` / `applications get` / `applications csv`
- `invite list` / `invite create`
- `score add` / `score cancel`

### Phase 3
- `schedules create` / `schedules publish` / `schedules qr`
- `forms create` / `forms get`
- `storage get` / `storage set`
- `members transfer` / `members status`
- `email send` / `email list`

## 10. AI Agent 친화 설계 원칙

1. **`--help`가 곧 문서**: Agent가 `mashup --help`, `mashup members --help`로 사용법을 스스로 파악
2. **`--json` 출력**: 구조화된 JSON으로 Agent가 파싱 가능
3. **종료 코드**: 성공 0, 인증 실패 1, API 에러 2, 입력 오류 3 → Agent가 결과 판단
4. **에러 메시지**: stderr로 에러, stdout은 순수 데이터만 → Agent 파싱에 노이즈 없음
5. **멱등성**: 같은 조회 명령은 항상 같은 포맷 반환

## 11. 범위 외 (Out of Scope)

- Member API (멤버 앱용) 래핑
- Recruit API (지원자용) 래핑
- MCP Server 형태 (추후 별도 프로젝트로)
- 웹 UI / 대시보드

## 12. 서버 API 추가 필요 사항

현재 Admin API에 없어서 CLI 기능을 완성하려면 서버에 추가해야 하는 엔드포인트.

### 12.1 출석 상태 변경 API

현재 출석 체크는 멤버 본인이 QR 코드로만 가능하다.
관리자가 출석 상태를 직접 변경할 수 있는 API가 없어서, 실수나 예외 상황에 대응할 수 없다.

**필요 엔드포인트** (mashup-admin):

```
PUT /api/v1/schedules/{scheduleId}/events/{eventId}/members/{memberId}/attendance
Body: { "status": "ATTENDANCE" | "LATE" | "ABSENT" }
```

**동작**:
- Attendance 레코드가 있으면 상태 변경 (`changeStatus`)
- Attendance 레코드가 없으면 새로 생성 (`Attendance.of`)
- 권한: Admin 로그인 필요

**사용 시나리오**:
- QR 인식 불량으로 출석 못한 멤버를 출석으로 변경
- 사유 있는 지각자를 출석으로 변경
- AI Agent가 리더 요청을 받아 자동으로 출석 상태 수정

### 12.2 출석 현황 조회 API

현재 Admin API에 플랫폼별 출석 현황을 조회하는 엔드포인트가 없다.
(Member API에만 존재: `GET /api/v1/attendance/platforms`)

**필요 엔드포인트** (mashup-admin):

```
GET /api/v1/schedules/{scheduleId}/attendance
Response: 플랫폼별 출석/지각/결석 현황 집계
```

```
GET /api/v1/schedules/{scheduleId}/attendance/members?platform=SPRING
Response: 특정 플랫폼 멤버별 출석 상태 목록
```
