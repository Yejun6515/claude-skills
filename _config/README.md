# _config — PC별 로컬 경로 설정

스킬은 여러 PC(회사·집·노트북·미니PC)에서 GitHub로 동기화해 쓴다.
SKILL.md 본문은 모든 PC에서 동일하게 유지하고, **PC마다 다른 경로만 이 폴더의
`local-paths.md` 한 파일**에 둔다. `local-paths.md`는 git에서 제외되므로(루트
.gitignore), 새 PC에서는 클론 후 이 파일 하나만 만들면 셋업 끝.

## local-paths.md 형식 — `키: 값` 한 줄씩

```
vault_root: C:\Users\<사용자>\Desktop\Yejun
tts_output_root: C:\Users\<사용자>\Desktop\TTS
mail_automation_root: C:\Users\<사용자>\Desktop\Workplace\메일 자동화
```

| 키 | 무엇 | 쓰는 스킬 |
|---|---|---|
| `vault_root` | Obsidian 볼트 루트 | note-digest · note-description · wiki-ingest · wiki-link · steel-project-wiki-context · tiro-meeting-note · mail-bridge · meeting-folder-brief · youtube-obsidian |
| `tts_output_root` | word-tts MP3 출력 루트 | word-tts |
| `mail_automation_root` | 메일 자동화 작업 폴더 (업무 PC에만 있음) | mail-bridge |

## 규칙

- 파일 또는 키가 없으면: 스킬이 사용자에게 물어 **이 파일에 저장**한 뒤 진행한다.
- 그 PC에 없는 자원(예: 집 PC의 메일 자동화 폴더)은 키를 생략한다 — 해당 스킬이
  그 키를 요구할 때 물어보게 된다.
- SKILL.md에 사용자 계정이 들어간 절대경로(`C:\Users\<계정>\...`)를 하드코딩하지
  않는다. 스킬 폴더 자신은 `<skillDir>`, 스킬 저장소 루트는
  `%USERPROFILE%\.claude\skills`(모든 PC 공통 클론 위치)로 표기한다.
