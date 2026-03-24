# Skill 导入检查清单

## 目标

将本地多个来源的 skills 归一化到当前仓库，并为后续 Gitee 与 npm/npx 分发做准备。

## 当前结论

- 已在仓库内存在并可分发：35 个 skill
- 可直接导入的普通 skill：30 个新增导入项，已全部导入
- 已归一化处理的聚合或多平台目录：2 组
- 仍需后续去重/决策的目录：`superpowers` 聚合目录

## 状态说明

- `already-in-repo`: 已在当前仓库中存在
- `imported`: 已导入当前仓库
- `ready-to-import`: 根目录直接包含 `SKILL.md`，适合直接导入
- `normalize-nested-layout`: 目录本身不是 skill 根，需要抽取内部真实 skill
- `duplicate-source`: 来源重复，后续导入时需去重

## 可直接导入项

| Source | Skill | Source Path | Status | Notes |
|---|---|---|---|---|
| `codex` | `architecture-review-checklist` | `C:\Users\tealiving\.codex\skills\architecture-review-checklist` | `imported` | 已导入 `skills/architecture-review-checklist` |
| `codex` | `chinese-code-comments` | `C:\Users\tealiving\.codex\skills\chinese-code-comments` | `imported` | 已导入 `skills/chinese-code-comments` |
| `codex` | `enterprise-layered-architecture` | `C:\Users\tealiving\.codex\skills\enterprise-layered-architecture` | `imported` | 已导入 `skills/enterprise-layered-architecture` |
| `codex` | `figma` | `C:\Users\tealiving\.codex\skills\figma` | `imported` | 已导入 `skills/figma` |
| `codex` | `git-report-summarizer` | `C:\Users\tealiving\.codex\skills\git-report-summarizer` | `already-in-repo` | 当前仓库已存在 |
| `codex` | `pdf` | `C:\Users\tealiving\.codex\skills\pdf` | `imported` | 已导入 `skills/pdf` |
| `codex` | `ppt-agent-llm-orchestration` | `C:\Users\tealiving\.codex\skills\ppt-agent-llm-orchestration` | `imported` | 已导入 `skills/ppt-agent-llm-orchestration` |
| `codex` | `pptx` | `C:\Users\tealiving\.codex\skills\pptx` | `imported` | 已导入 `skills/pptx` |
| `codex` | `pptx-generator` | `C:\Users\tealiving\.codex\skills\pptx-generator` | `imported` | 已导入 `skills/pptx-generator` |
| `codex` | `pyqt-fluent-ui-design` | `C:\Users\tealiving\.codex\skills\pyqt-fluent-ui-design` | `imported` | 已导入 `skills/pyqt-fluent-ui-design` |
| `codex` | `python-enterprise-development` | `C:\Users\tealiving\.codex\skills\python-enterprise-development` | `imported` | 已导入 `skills/python-enterprise-development` |
| `agents` | `better-auth-best-practices` | `C:\Users\tealiving\.agents\skills\better-auth-best-practices` | `imported` | 已导入 `skills/better-auth-best-practices` |
| `agents` | `find-skills` | `C:\Users\tealiving\.agents\skills\find-skills` | `imported` | 已导入 `skills/find-skills` |
| `agents` | `frontend-design` | `C:\Users\tealiving\.agents\skills\frontend-design` | `imported` | 已导入 `skills/frontend-design` |
| `agents` | `python-project-structure` | `C:\Users\tealiving\.agents\skills\python-project-structure` | `imported` | 已导入 `skills/python-project-structure` |
| `agents` | `ui-ux-pro-max` | `C:\Users\tealiving\.agents\skills\ui-ux-pro-max` | `imported` | 已导入 `skills/ui-ux-pro-max` |
| `agents` | `xlsx` | `C:\Users\tealiving\.agents\skills\xlsx` | `imported` | 已导入 `skills/xlsx` |
| `superpowers` | `brainstorming` | `C:\Users\tealiving\.codex\superpowers\skills\brainstorming` | `imported` | 已导入 `skills/brainstorming` |
| `superpowers` | `dispatching-parallel-agents` | `C:\Users\tealiving\.codex\superpowers\skills\dispatching-parallel-agents` | `imported` | 已导入 `skills/dispatching-parallel-agents` |
| `superpowers` | `executing-plans` | `C:\Users\tealiving\.codex\superpowers\skills\executing-plans` | `imported` | 已导入 `skills/executing-plans` |
| `superpowers` | `finishing-a-development-branch` | `C:\Users\tealiving\.codex\superpowers\skills\finishing-a-development-branch` | `imported` | 已导入 `skills/finishing-a-development-branch` |
| `superpowers` | `receiving-code-review` | `C:\Users\tealiving\.codex\superpowers\skills\receiving-code-review` | `imported` | 已导入 `skills/receiving-code-review` |
| `superpowers` | `requesting-code-review` | `C:\Users\tealiving\.codex\superpowers\skills\requesting-code-review` | `imported` | 已导入 `skills/requesting-code-review` |
| `superpowers` | `subagent-driven-development` | `C:\Users\tealiving\.codex\superpowers\skills\subagent-driven-development` | `imported` | 已导入 `skills/subagent-driven-development` |
| `superpowers` | `systematic-debugging` | `C:\Users\tealiving\.codex\superpowers\skills\systematic-debugging` | `imported` | 已导入 `skills/systematic-debugging` |
| `superpowers` | `test-driven-development` | `C:\Users\tealiving\.codex\superpowers\skills\test-driven-development` | `imported` | 已导入 `skills/test-driven-development` |
| `superpowers` | `using-git-worktrees` | `C:\Users\tealiving\.codex\superpowers\skills\using-git-worktrees` | `imported` | 已导入 `skills/using-git-worktrees` |
| `superpowers` | `using-superpowers` | `C:\Users\tealiving\.codex\superpowers\skills\using-superpowers` | `imported` | 已导入 `skills/using-superpowers` |
| `superpowers` | `verification-before-completion` | `C:\Users\tealiving\.codex\superpowers\skills\verification-before-completion` | `imported` | 已导入 `skills/verification-before-completion` |
| `superpowers` | `writing-plans` | `C:\Users\tealiving\.codex\superpowers\skills\writing-plans` | `imported` | 已导入 `skills/writing-plans` |
| `superpowers` | `writing-skills` | `C:\Users\tealiving\.codex\superpowers\skills\writing-skills` | `imported` | 已导入 `skills/writing-skills` |

## 需要归一化的目录

| Source | Directory | Source Path | Status | Notes |
|---|---|---|---|---|
| `codex` | `.system` | `C:\Users\tealiving\.codex\skills\.system` | `imported` | 已拆分导入 `openai-docs`、`skill-creator`、`skill-installer` |
| `codex` | `planning-with-files` | `C:\Users\tealiving\.codex\skills\planning-with-files` | `imported` | 已抽取 Codex 对应子目录并导入 `skills/planning-with-files` |
| `codex` | `superpowers` | `C:\Users\tealiving\.codex\skills\superpowers` | `duplicate-source` | 与 `C:\Users\tealiving\.codex\superpowers\skills\*` 显式目录重复，优先后者 |

## 建议导入顺序

1. 已导入根目录直接包含 `SKILL.md` 的普通 skill
2. 已处理 `.system` 和 `planning-with-files` 这类嵌套结构
3. 下一步处理 `superpowers` 聚合目录去重和发布文档收口

## 下一步

- 为 `.system` 和 `planning-with-files` 增加 catalog 记录并补齐 README 索引
- 处理 `superpowers` 聚合目录的去重说明
- 准备内网 Gitee 与 npm 发布文档
