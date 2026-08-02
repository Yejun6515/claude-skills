# 글로벌 규칙 (3대 PC 공통)

이 파일이 본체다. 각 PC의 `~/.claude/CLAUDE.md`가 한 줄로 임포트한다.
**수정은 이 파일에서만** 하고 push → 다른 PC는 pull. 새 PC 셋업은 `../README.md` 참조.

여기엔 **모든 PC에서 항상 참인 것만** 적는다. PC마다 다른 경로·설치 상태는
`local-paths.md`(gitignore) 또는 각 PC의 메모리에 둔다.

## 대화

- 한국어로 답한다.
- 음성 입력(Typeless)을 주로 쓴다. 문맥에 안 맞는 생뚱맞은 단어가 나오면 오타가 아니라
  **음성 오인식**으로 보고, 발음이 비슷한 영어 약어·기술 용어로 해석한다
  (예: "Typeless" → TTS, "cloud.md" → CLAUDE.md). 확신 없으면 가볍게 확인하고 진행.

## 머신 3대

집 노트북 · 회사 PC(사용자명 `Z006K14G`) · 미니PC(`nucbox-g10`, Tailscale `100.115.42.64`).

- **절대경로를 하드코딩하지 않는다** — 사용자명이 PC마다 다르다.
  `%USERPROFILE%` 또는 `_config/local-paths.md`의 키(`vault_root` 등)를 쓴다.
- 24시간 상시 운영(봇·Eagle 등)은 미니PC 담당. 노트북·회사 PC는 개발·편집용.

## 새 코딩 프로젝트

- 파일을 만들거나 `git init` 하기 **전에 "폴더 어디서 시작할까요?"를 먼저 묻는다.**
- 기본 위치는 PC마다 다르다 → `_config/local-paths.md`의 `project_root` 키.
- GitHub 업로드·백업은 **명시적으로 요청할 때만** 한다.

## 스킬 저장소

- `%USERPROFILE%\.claude\skills` 폴더 자체가 `Yejun6515/claude-skills` 레포다.
  모든 PC의 클론 위치가 같다. **스킬 수정은 이 한 곳에서만**(분기 방지).
- "github에 올려줘" → 이 폴더에서 `git add -A && git commit && git push`.
- SKILL.md에 PC별 경로를 쓰지 않는다 → `_config/local-paths.md`로 뺀다.

## 동기화되는 것 / 안 되는 것

- **동기화됨**: `~/.claude/skills` 안의 모든 것(스킬·이 파일·`_scripts`).
- **안 됨**: `settings.json`·훅·`statusline.ps1`·메모리·`local-paths.md`.
  → 새 PC에서는 PC마다 1회 수동 설정이 필요하다.
- **메모리는 PC별 로컬**이며 세션 시작 폴더별로도 분리된다. 3대가 공통으로 알아야 할
  사실이면 메모리에 두지 말고 이 파일이나 스킬 레포 문서로 올린다.

## Windows / PowerShell 5.1

- 비ASCII 문자열을 셸 파이프로 넘기면 깨진다 → UTF-8 스크립트 파일로 실행할 것.
- PowerShell 5.1에는 `&&`·`??`·삼항 연산자가 없다. 경로에 공백이 있으면 반드시 인용.
- native exe에 stdin을 파이프하면 인코딩이 깨져 인증 토큰 등이 손상된다.

## 산출물

- 파일은 **BOM 없는 UTF-8**, 날짜는 `YYYY-MM-DD`.
- Obsidian 볼트 작업 규칙은 볼트 루트의 `CLAUDE.md`에 있다(경로는 `vault_root` 키).
