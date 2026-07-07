# 플러그인 통일 목록 (모든 PC 공통)

새 PC에서 아래를 설치하면 플러그인이 통일된다. 정식 방법은 Claude Code에서 슬래시 명령:

```
/plugin marketplace add <repo>
/plugin install <플러그인>@<마켓플레이스>
```

수동 등록(헤드리스 등 슬래시 명령을 못 쓸 때)은 두 파일을 직접 편집:
- `%USERPROFILE%\.claude\plugins\known_marketplaces.json` — 마켓플레이스 등록
- `%USERPROFILE%\.claude\settings.json` 의 `enabledPlugins` — `"플러그인@마켓플레이스": true`
- 마켓플레이스 repo는 `%USERPROFILE%\.claude\plugins\marketplaces\<마켓플레이스이름>` 에 clone
- 편집 후 Claude Code 재시작 필요.

## 마켓플레이스

| 이름 | repo |
|---|---|
| `claude-plugins-official` | `anthropics/claude-plugins-official` (기본 제공) |
| `superpowers-dev` | `obra/superpowers` |
| `understand-anything` | `Egonex-AI/Understand-Anything` |

## 설치할 플러그인

| 플러그인 | 마켓플레이스 | 비고 |
|---|---|---|
| `superpowers` | `superpowers-dev` | TDD·디버깅·협업 패턴 스킬 라이브러리 (v6.1.1, 스킬 14개 + 세션시작 훅) |
| `understand-anything` | `understand-anything` | 코드베이스 분석·지식그래프·대시보드 (v2.8.2, 스킬 8개). **TS/대시보드 기능은 pnpm 빌드 필요**(Node≥22, pnpm≥10). 마켓플레이스 폴더에서 `pnpm install` → `pnpm --filter @understand-anything/core build` → `pnpm --filter @understand-anything/skill build`, 대시보드는 `pnpm --filter @understand-anything/dashboard build`. |

<!-- 다른 PC(회사/노트북)에서 쓰는 플러그인을 확인하면 여기에 추가 -->
