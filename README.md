# claude-skills

예준님의 Claude Code 스킬 모음. 회사 PC·집 PC·노트북·미니PC에서 **같은 스킬**을 쓰기 위해
GitHub로 동기화한다. 클론 위치는 모든 PC 공통: `%USERPROFILE%\.claude\skills`.

## 새 PC 셋업

1. 클론:
   ```
   git clone https://github.com/Yejun6515/claude-skills.git "%USERPROFILE%\.claude\skills"
   ```
2. `_config\local-paths.md` 생성 — 이 PC의 경로(볼트 루트 등)를 적는다. 형식·키 목록은 `_config\README.md`.
3. (Obsidian 볼트가 있는 PC) push/pull 후 `_scripts\update-index.ps1` 실행 → 볼트의 스킬 인덱스 노트 갱신.

## 리포 규칙

- **PC별 경로는 SKILL.md에 하드코딩하지 않는다** — `_config\local-paths.md`(gitignore됨)로 뺀다.
- agentmemory 플러그인 스킬(recall/remember/handoff 등)은 플러그인이 설치하므로 repo에서 제외(.gitignore).
- 볼트 태그 어휘(`entity/`·`topic/`)의 마스터는 `note-description\SKILL.md`의 controlled vocabulary — 새 태그는 반드시 거기에 추가.
- 스킬별 최신 설명은 각 `SKILL.md` frontmatter가 정본이고, 한눈 목록은 볼트 `07. Claude Skills` 인덱스 노트(`update-index.ps1`이 자동 생성)에서 본다.

## 스킬 한눈에 (카테고리)

| 분류 | 스킬 |
|---|---|
| 견적·영업 (PTJ) | `견적서-작성` `ptj-internal-estimate` `breakdown-rev-compare` `mail-bridge` `travel-schedule-excel` |
| Obsidian 볼트·위키 | `note-digest` `note-description` `tiro-meeting-note` `meeting-folder-brief` `wiki-ingest` `wiki-link` `steel-project-wiki-context` `youtube-obsidian` |
| 브랜드·문서 | `primetals-text-style` `word-mom-translate` |
| 일본어 학습 | `word-tts` `jp-drama-excel` `jp-smartglass-vocab` `anki-mp3-rename` |
| 도구 | `_scripts\update-index.ps1`(인덱스 갱신) · `_scripts\notify-done.ps1`(완료 알람 훅) |
