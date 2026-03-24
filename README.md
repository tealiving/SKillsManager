# SKillsManager

用于集中管理、归档与分发多个 Codex skills。

## What This Repo Stores

- `skills/`: 各个独立 skill 的完整目录
- `catalog/skills.json`: 可分发 skills 清单与安装元数据
- `docs/plans/`: 迁移、分发、实施计划文档

## Distribution Model

本仓库同时承担两个角色：

- 源码仓库：维护每个 skill 的目录、模板、脚本和文档
- 分发仓库：为后续内网 Gitee 与 npm/npx 安装入口提供统一目录和 manifest

推荐的用户安装方式会是：

```bash
npx @your-org/codex-skills list
npx @your-org/codex-skills install <skill-name>
```

在 npm 入口未就绪前，可继续通过仓库脚本或手工复制目录安装到 `%USERPROFILE%\\.codex\\skills`。

更多说明见：

- `docs/usage/install.md`
- `docs/usage/publish.md`
- `docs/release-checklist.md`

## Skills Index

当前仓库已导入 35 个可直接安装的 skills。

| Skill | 目录 | 来源 | 人类入口 | Agent 入口 | 分发状态 |
|---|---|---|---|---|---|
| `architecture-review-checklist` | `skills/architecture-review-checklist/` | `codex` | `-` | `SKILL.md` | `installable` |
| `better-auth-best-practices` | `skills/better-auth-best-practices/` | `agents` | `-` | `SKILL.md` | `installable` |
| `brainstorming` | `skills/brainstorming/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `chinese-code-comments` | `skills/chinese-code-comments/` | `codex` | `-` | `SKILL.md` | `installable` |
| `dispatching-parallel-agents` | `skills/dispatching-parallel-agents/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `enterprise-layered-architecture` | `skills/enterprise-layered-architecture/` | `codex` | `-` | `SKILL.md` | `installable` |
| `executing-plans` | `skills/executing-plans/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `figma` | `skills/figma/` | `codex` | `-` | `SKILL.md` | `installable` |
| `find-skills` | `skills/find-skills/` | `agents` | `-` | `SKILL.md` | `installable` |
| `finishing-a-development-branch` | `skills/finishing-a-development-branch/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `frontend-design` | `skills/frontend-design/` | `agents` | `-` | `SKILL.md` | `installable` |
| `git-report-summarizer` | `skills/git-report-summarizer/` | `codex` | `README.md` | `SKILL.md` | `installable` |
| `openai-docs` | `skills/openai-docs/` | `codex-system` | `-` | `SKILL.md` | `installable` |
| `planning-with-files` | `skills/planning-with-files/` | `codex-nested` | `-` | `SKILL.md` | `installable` |
| `pdf` | `skills/pdf/` | `codex` | `-` | `SKILL.md` | `installable` |
| `ppt-agent-llm-orchestration` | `skills/ppt-agent-llm-orchestration/` | `codex` | `-` | `SKILL.md` | `installable` |
| `pptx` | `skills/pptx/` | `codex` | `-` | `SKILL.md` | `installable` |
| `pptx-generator` | `skills/pptx-generator/` | `codex` | `-` | `SKILL.md` | `installable` |
| `pyqt-fluent-ui-design` | `skills/pyqt-fluent-ui-design/` | `codex` | `-` | `SKILL.md` | `installable` |
| `python-enterprise-development` | `skills/python-enterprise-development/` | `codex` | `-` | `SKILL.md` | `installable` |
| `python-project-structure` | `skills/python-project-structure/` | `agents` | `-` | `SKILL.md` | `installable` |
| `receiving-code-review` | `skills/receiving-code-review/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `requesting-code-review` | `skills/requesting-code-review/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `skill-creator` | `skills/skill-creator/` | `codex-system` | `-` | `SKILL.md` | `installable` |
| `skill-installer` | `skills/skill-installer/` | `codex-system` | `-` | `SKILL.md` | `installable` |
| `subagent-driven-development` | `skills/subagent-driven-development/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `systematic-debugging` | `skills/systematic-debugging/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `test-driven-development` | `skills/test-driven-development/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `ui-ux-pro-max` | `skills/ui-ux-pro-max/` | `agents` | `-` | `SKILL.md` | `installable` |
| `using-git-worktrees` | `skills/using-git-worktrees/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `using-superpowers` | `skills/using-superpowers/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `verification-before-completion` | `skills/verification-before-completion/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `writing-plans` | `skills/writing-plans/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `writing-skills` | `skills/writing-skills/` | `superpowers` | `-` | `SKILL.md` | `installable` |
| `xlsx` | `skills/xlsx/` | `agents` | `-` | `SKILL.md` | `installable` |

## Planned Catalog Governance

- 所有可安装 skill 统一落在 `skills/<skill-name>/`
- 只有实际存在于仓库中的 skill 才进入 `catalog/skills.json`
- 本地来源盘点、去重和待导入项记录在 `docs/plans/2026-03-24-skill-import-checklist.md`
- 新增或删除 skill 时，同时更新本页的 `Skills Index` 和 `catalog/skills.json`
- `C:\Users\tealiving\.codex\skills\superpowers` 聚合目录当前不再单独导入，因为其内容已由 `C:\Users\tealiving\.codex\superpowers\skills\*` 显式目录覆盖

## Suggested README Pattern

父层 `README.md` 建议承担“索引页 + 分发入口”职责：

- 说明仓库用途
- 用表格列出所有 skill 的目录和功能
- 提供人类入口与 agent 入口
- 说明默认安装命令和安装目录
- 约定新增 skill 时同步更新索引与 manifest

子目录建议分工如下：

- `README.md`：给人看，说明用途、目录结构、常用命令、输出物
- `SKILL.md`：给 agent 用，描述触发条件和执行工作流

## Maintenance Rule

新增或删除 skill 时，同时更新本页的 `Skills Index` 表格和 `catalog/skills.json`。
