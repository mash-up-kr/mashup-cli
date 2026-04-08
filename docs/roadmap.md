# Roadmap

## 현재 구현 상태

### 완료

| 커맨드 | 비고 |
|--------|------|
| `login` / `whoami` / `logout` | |
| `members list` / `get` / `reset-password` / `status` / `transfer` | |
| `generations list` / `create` | |
| `schedules list` / `get` / `publish` / `hide` / `qr` | |
| `applications list` / `get` / `update-result` / `csv` | 단건 update-result만 구현 |
| `push broadcast` / `narrowcast` | |
| `invite list` / `create` | |
| `score add` / `cancel` | |
| `storage get` / `set` / `keys` | |
| `--json` 글로벌 옵션 | |

---

## 추후 구현 범위

### 1. 출석 일괄 변경 (서버 API 추가 선행 필요)

**시나리오**: 운영진이 기수·플랫폼·이름 목록을 입력해 여러 멤버의 출석 상태를 한 번에 변경한다.

```bash
mashup attendance bulk \
  --generation 14 \
  --date 2026-04-08 \
  --platform SPRING \
  --names "홍길동,김철수,이영희" \
  --status ATTENDANCE
```

**내부 동작**:
1. `schedules list <generation>` → 날짜로 scheduleId 자동 조회
2. `members list <generation> --platform` → 이름으로 memberId 매핑
3. 각 memberId마다 출석 상태 변경 API 순차 호출

**선행 서버 작업** ([PRD §12](../mashup-cli-prd.md) 참조):

```
PUT /api/v1/schedules/{scheduleId}/events/{eventId}/members/{memberId}/attendance
Body: { "status": "ATTENDANCE" | "LATE" | "ABSENT" }
```

---

### 2. 출석 현황 조회 (서버 API 추가 선행 필요)

```bash
mashup attendance list <scheduleId>                          # 플랫폼별 출석 집계
mashup attendance list <scheduleId> --platform SPRING        # 플랫폼별 멤버 출석 목록
mashup attendance get <scheduleId> <memberId>                # 멤버 개인 출석 상태
```

**선행 서버 작업**:

```
GET /api/v1/schedules/{scheduleId}/attendance
GET /api/v1/schedules/{scheduleId}/attendance/members?platform=SPRING
```

---

### 3. 일정 생성 (인터랙티브)

```bash
mashup schedules create
```

이벤트를 여러 개 구성해야 해서 단순 플래그 방식이 어렵다.
인터랙티브 프롬프트 or `--file schedule.json` 방식으로 구현 예정.

---

### 4. 미구현 커맨드

| 커맨드 | 비고 |
|--------|------|
| `teams list` / `create` | 커맨드 누락 |
| `applications update-result` (bulk) | 현재 단건만 구현됨 |
| `forms list` / `get` / `create` | 설문 문항 중첩 구조로 UX 설계 필요 |
| `email send` / `list` | |

---

## 참고: 플랫폼 고정값

서버에 플랫폼 목록 API가 없으므로 CLI에 하드코딩.

```
SPRING, iOS, WEB, ANDROID, NODE
```

## 참고: 이름 검색 제약

`members list`는 기수 번호가 필수다. 기수 없이 전체에서 이름 검색하려면 서버 API 추가가 필요하다.
