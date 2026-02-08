# Agent Documentation Standards

## 0. Communication Language
**All agent responses MUST be written in Korean (한글).**
- Task descriptions, analysis, documentation - everything in Korean
- Only code, file paths, and technical identifiers in English
- 모든 에이전트 응답은 한글로 작성되어야 합니다

## 1. Obsidian Integration

### 1.1 Vault Structure (단순화된 구조)
All agent-generated Markdown files MUST be created in the Obsidian vault with the following simplified structure:

```
Obsidian Vault/
├── Tasks/                 # Task 관리
│   ├── Kanban.md         # 메인 칸반 보드
│   └── {YYYY-MM-DD}-{title}.md  # 개별 task 상세
├── Docs/                  # 문서
│   ├── Architecture/     # 아키텍처 문서
│   └── Analysis/         # 분석 결과
└── Templates/             # 템플릿
    └── task-template.md
```

**Note**: 1인 개발 및 단순 스크립트 프로젝트에 최적화된 구조입니다.

### 1.2 File Naming Conventions
- **Tasks**: `{YYYY-MM-DD}-{간단한-제목}.md` (예: `2026-02-08-슬랙봇-인증-구현.md`)
- **Architecture**: `{topic}.md` (예: `현재-아키텍처-분석.md`)
- **Analysis**: `{YYYY-MM-DD}-{주제}.md` (예: `2026-02-08-성능-분석.md`)
- 파일명은 한글-영문 혼용 가능, kebab-case 사용
- 특수문자는 하이픈(-)만 사용

### 1.3 Frontmatter Standards
All documents MUST include YAML frontmatter (한글로 작성):

```yaml
---
생성일: YYYY-MM-DD HH:mm
수정일: YYYY-MM-DD HH:mm
타입: [task|architecture|analysis]
상태: [대기|진행중|검토|완료|보류]
태그: [관련, 태그, 여기]
담당: [agent-name]
관련문서: [[링크-to-관련-문서]]
---
```

## 2. Document Classification System

### 2.1 Document Types (단순화)

#### Tasks (`Tasks/`)
개별 task 명세 및 상세 지침 (한글로 작성)

**Template Structure** (한글 작성):
```markdown
---
생성일: YYYY-MM-DD HH:mm
수정일: YYYY-MM-DD HH:mm
타입: task
상태: [대기|진행중|보류|검토|완료]
우선순위: [긴급|높음|보통|낮음]
담당: [agent-name]
예상시간: X시간
태그: [기능, 백엔드, API]
관련문서: [[상위-task]], [[의존-task]]
---

# {Title}

## 배경
이 작업이 필요한 이유와 맥락을 간단히 설명

## 목표
- 주요 목표 1
- 주요 목표 2

## 완료 조건
- [ ] 조건 1
- [ ] 조건 2
- [ ] 조건 3

## 기술 접근 방법
상세한 기술적 방향과 구현 전략 (한글로 작성)

## 의존성
- [[TASK-XXX]]: 의존성 설명
- 외부 의존성: 설명

## 위험 요소
| 위험 | 영향도 | 대응방안 |
|------|--------|----------|
| ... | ... | ... |

## 참고 자료
- [문서](url)
- 관련 코드: `path/to/file.py`

## 진행 로그
### YYYY-MM-DD HH:mm - Agent Name
- 진행 상황 업데이트 (한글로)

## 메모
추가 메모 및 관찰 사항 (한글로)
```

#### Architecture (`Docs/Architecture/`)
아키텍처 결정 및 설계 문서 (한글 작성)

#### Analysis (`Docs/Analysis/`)
조사 결과, 성능 분석, 코드 리뷰 (한글 작성)

### 2.2 Cross-Referencing
- 내부 문서 참조는 `[[WikiLinks]]` 사용
- 분류용 태그: `#백엔드`, `#프론트엔드`, `#긴급`
- 관련 문서 간 양방향 링크 유지

## 3. Kanban Board Management

### 3.1 Main Kanban Board (`Tasks/Kanban.md`)

**한글로 작성된 칸반 보드**:

```markdown
---
생성일: YYYY-MM-DD
수정일: YYYY-MM-DD
타입: kanban
태그: [칸반, 작업관리]
---

# 프로젝트 칸반 보드

## 📝 Backlog
- [[2026-02-08-슬랙봇-인증]] #우선순위-높음 @agent-claude
- [[2026-02-08-데이터-파싱]] #우선순위-보통 @agent-gemini

## 📋 Todo
- [[2026-02-09-API-연동]] #우선순위-높음 @agent-claude
  - 의존성: [[2026-02-08-슬랙봇-인증]]
- [[2026-02-09-로깅-개선]] #우선순위-낮음 @agent-gemini

## 🔄 진행중
- [[2026-02-08-설정-파일-구조화]] #우선순위-긴급 @agent-claude
  - 시작: 2026-02-08
  - 진행률: 60%
  - 메모: API 키 설정 필요

## 👀 검토
- [[2026-02-07-에러-핸들링]] #우선순위-보통 @agent-claude
  - 완료: 2026-02-08
  - 검토 필요

## ✅ 완료
- [[2026-02-07-초기-구조]] #우선순위-높음 @agent-gemini
  - 완료: 2026-02-07

## 🚧 보류
- [[2026-02-08-외부-API-연동]] #우선순위-높음 @agent-claude
  - 차단 원인: 외부 API 접근 권한 대기중

---

## 📊 통계
- 전체 작업: 6개
- 완료: 1개
- 진행중: 1개
- 보류: 1개

## 👥 Agent 작업량
- @agent-claude: 4개 작업 (1개 진행중)
- @agent-gemini: 2개 작업
```

### 3.2 Kanban Update Protocol
1. **작업 생성**: Backlog에 추가, frontmatter 작성
2. **작업 할당**: Todo로 이동, agent 할당
3. **작업 시작**: 진행중으로 이동, 시작일 기록
4. **작업 완료**: 검토로 이동, 완료일 기록
5. **최종 완료**: 검토 후 완료로 이동
6. **작업 보류**: 보류로 이동, 차단 원인 문서화

### 3.3 Automated Kanban Updates
Agents는 다음 상황에서 반드시 칸반 보드를 업데이트해야 함:
- 새 작업 생성 시
- 작업 상태 변경 시
- 작업 완료 시
- 차단 요소 발견 시
- 작업 재할당 시

## 4. Multi-Agent Collaboration

**Important**: 모든 agent는 응답을 한글로 작성해야 합니다.

### 4.1 Agent Types

#### Claude CLI Agent
- **강점**: 복잡한 추론, 아키텍처 설계, 코드 품질
- **주요 작업**: 설계, 리팩토링, 복잡한 구현
- **식별자**: `@agent-claude`
- **언어**: 한글 응답 필수

#### Gemini Agent
- **강점**: 빠른 실행, 데이터 처리, 병렬 작업
- **주요 작업**: 데이터 분석, 배치 작업, 테스팅
- **식별자**: `@agent-gemini`
- **언어**: 한글 응답 필수

### 4.2 Task Assignment Strategy (간소화)

**복잡도 기준**:
- 긴급/높음 복잡도 → Claude
- 보통 복잡도 → 가용한 agent
- 낮은 복잡도 → Gemini 또는 가용한 agent

**도메인 기준**:
- 아키텍처/설계 → Claude
- 데이터 처리 → Gemini
- 구현 → 복잡도에 따라 배분
- 테스팅 → Gemini
- 문서화 → 모두 (한글로)

### 4.3 Concurrency Control (간소화)

#### Task Dependencies (frontmatter에 명시)
```yaml
의존성:
  - 작업: 2026-02-08-슬랙봇-인증
    타입: [차단중|차단됨|관련]
    상태: [대기|준비|완료]
```

#### Conflict Resolution (충돌 해결)
1. **예방**: 작업 시작 전 칸반 보드 확인
2. **감지**: 동시 수정 모니터링
3. **해결**:
   - 코드: 먼저 커밋한 것 우선
   - 문서: 병합
   - 충돌 발생 시: 사용자에게 에스컬레이션

### 4.4 Communication Protocol (간소화)

#### Task Handoff (작업 인계)
작업 인계 시 체크리스트:
- [ ] 작업 상태 업데이트
- [ ] 현재 진행 상황 문서화 (한글로)
- [ ] 남은 작업 목록 작성
- [ ] 차단 요소 기록
- [ ] 칸반 보드 업데이트
- [ ] Task 파일에 인계 메모 추가

## 5. Document Lifecycle (간소화)

### 5.1 Creation (생성)
1. 문서 타입 결정 및 적절한 디렉토리 선택
2. `Templates/` 에서 템플릿 사용
3. Frontmatter 작성 (한글로)
4. 초기 내용 작성 (한글로)
5. Task인 경우 칸반 보드에 링크
6. 관련 문서와 양방향 링크 생성

### 5.2 Updates (업데이트)
1. Frontmatter의 `수정일` 타임스탬프 업데이트
2. 진행 로그 항목 추가 (task의 경우, 한글로)
3. 상태 변경 시 업데이트
4. 상태 변경 시 칸반 보드 업데이트

### 5.3 Archival (보관)
1. 상태를 `완료`로 업데이트
2. 칸반 보드의 완료 섹션에 유지
3. 필요시 별도 보관 (1인 개발이므로 선택사항)

## 6. Quality Standards

### 6.1 Required Elements (필수 요소)
모든 문서는 반드시 포함:
- [ ] 완전한 YAML frontmatter (한글로)
- [ ] 명확한 제목과 목적 (한글로)
- [ ] 적절한 분류 (디렉토리 + 태그)
- [ ] 관련 문서 링크
- [ ] 담당 agent 표시

### 6.2 Task-Specific Requirements
Task 문서는 반드시 포함 (한글 작성):
- [ ] 명확한 완료 조건
- [ ] 기술적 접근 방법/방향
- [ ] 의존성 목록
- [ ] 위험 요소 평가
- [ ] 진행 로그

### 6.3 Review Criteria (완료 기준)
작업을 완료로 표시하기 전:
- [ ] 모든 완료 조건 충족
- [ ] 문서 업데이트 완료
- [ ] 테스트 통과
- [ ] 칸반 보드 업데이트
- [ ] 관련 작업 업데이트

## 7. Templates (간소화)

### 7.1 Available Templates
`Templates/` 디렉토리의 템플릿:
- `task-template.md` - 표준 작업 명세 (한글)

### 7.2 Template Usage
Agents는:
1. 적절한 템플릿 복사
2. 모든 섹션 작성 (한글로)
3. 불필요한 선택 섹션 제거 가능
4. 일관된 구조 유지

## 8. Best Practices (모범 사례)

### 8.1 General Guidelines (일반 지침)
- **한글 작성**: 모든 내용은 한글로 명확하게 작성
- 간결하고 실행 가능한 내용 작성
- 일관된 포맷과 구조 유지
- 관련 문서에 적극적으로 링크
- 칸반 보드를 실시간으로 업데이트
- 결정 사항과 근거를 문서화

### 8.2 Multi-Agent Coordination (다중 에이전트 협업)
- 작업 시작 전 칸반 보드 확인
- 의존성 존중
- 차단 요소 즉시 소통
- 진행 상황 정기적 업데이트 (한글로)
- 완전한 컨텍스트와 함께 작업 인계

### 8.3 Maintenance (유지보수)
- 완료된 작업 정기 검토 (1인 개발이므로 유연하게)
- 학습 내용 기반으로 템플릿 업데이트
- 깔끔한 디렉토리 구조 유지
- 칸반 보드 최신 상태 유지

---

## Appendix A: Quick Reference (빠른 참조)

### Task Creation Workflow (작업 생성 흐름)
1. Task 파일 생성: `Tasks/{YYYY-MM-DD}-{제목}.md`
2. 템플릿 사용하여 frontmatter와 내용 작성 (한글로)
3. 칸반 보드(Backlog)에 추가
4. 관련 문서 링크 생성
5. 담당 agent 할당 (알고 있는 경우)

### Kanban Update Commands (칸반 업데이트 명령)
- 새 작업 → Backlog에 추가
- 시작 준비 → Todo로 이동
- 작업 시작 → 진행중으로 이동
- 검토 필요 → 검토로 이동
- 작업 완료 → 완료로 이동
- 진행 불가 → 보류로 이동

### Document Type Selection (문서 타입 선택)
- 기능 구현 → Task (한글로 작성)
- 아키텍처 결정 → Architecture (한글로 작성)
- 이슈 조사 → Analysis (한글로 작성)

---

## 📌 중요 원칙

1. **모든 에이전트 응답은 한글로 작성**
2. **단순 스크립트 프로젝트에 적합한 간소화된 구조**
3. **1인 개발 환경 고려**
4. **칸반 보드 중심의 작업 관리**
5. **실용적이고 실행 가능한 문서화**